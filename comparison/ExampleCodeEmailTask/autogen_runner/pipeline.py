"""AutoGen-based baseline with a lightweight two-agent conversation (Groq)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

from common.cost_model import estimate_cost_usd
from common.dataset import load_labels
from common.email_schema import ClassificationResult, EmailRecord, PerEmailMetrics, TokenUsage
from common.io_utils import load_yaml
from common.timing import RateLimiter, measure_latency_ms
from autogen_runner.agents import EmailAssistantAgent, ReviewerAgent


class AutoGenClassifier:
    """Coordinate a short AutoGen conversation to classify an email."""

    def __init__(self, config_dir: Path):
        """Initialize AutoGen agents, configuration, and HTTP client."""
        self.config_dir = config_dir
        self.providers = load_yaml(config_dir / "providers.yaml")
        self.labels_config = load_labels(config_dir)
        self.label_names = [item["name"] for item in self.labels_config]
        # Track cumulative wait time (rate limiting, retries) per email for reporting.
        self.wait_seconds = 0.0

        groq_cfg = self.providers.get("groq", {}).get("autogen", {})
        self.provider = "groq"
        self.model_name = groq_cfg.get("model") or groq_cfg.get("model_id") or "llama-3.1-8b-instant"
        self.api_key_env = groq_cfg.get("env_var", "GROQ_API_KEY")
        self.base_url = self.providers.get("groq", {}).get("base_url", "https://api.groq.com/openai/v1")
        if not self.api_key_env:
            raise ValueError("Missing env_var for AutoGen client")
        self.api_key = os.getenv(self.api_key_env)
        if not self.api_key:
            raise EnvironmentError(f"Environment variable {self.api_key_env} must be set")

        self.session = requests.Session()
        self.assistant = EmailAssistantAgent(self.provider)
        self.reviewer = ReviewerAgent(self.provider)
        self.provider_label = f"{self.provider}:{self.model_name}"
        rpm = int(groq_cfg.get("max_requests_per_minute") or 0)
        self.rate_limiter = RateLimiter(rpm)

    def classify(self, email: EmailRecord) -> Tuple[ClassificationResult, PerEmailMetrics]:
        """Run the assistant + reviewer conversation for an email."""
        # Reset wait accumulator for this email so per-email metrics stay accurate.
        self.wait_seconds = 0.0
        with measure_latency_ms() as timer:
            assistant_text, reviewer_text, total_usage = self._invoke_assistant_and_reviewer(email)
            if total_usage is None:
                raise RuntimeError("AutoGen conversation did not produce token usage")

        latency_ms = timer.get("elapsed_ms", 0.0)
        wait_ms = self.wait_seconds * 1000.0
        actual_runtime_ms = max(latency_ms - wait_ms, 0.0)
        final_text = reviewer_text or assistant_text
        parsed = self._parse_output(final_text)
        label = self._normalize_label(parsed.get("label", self.label_names[0] if self.label_names else ""))
        is_correct = label == email.true_label
        cost_usd = estimate_cost_usd(total_usage, self.model_name)

        classification = ClassificationResult(
            email_id=email.id,
            predicted_label=label,
            method="autogen",
            raw_response={"assistant": assistant_text, "reviewer": reviewer_text, "parsed": parsed, "from_llm": True},
        )
        metrics = PerEmailMetrics(
            email_id=email.id,
            true_label=email.true_label,
            predicted_label=label,
            method="autogen",
            latency_ms=latency_ms,
            wait_ms=wait_ms,
            actual_runtime_ms=actual_runtime_ms,
            token_usage=total_usage,
            cost_usd=cost_usd,
            layers_used=None,
            is_correct=is_correct,
        )
        return classification, metrics

    def _build_assistant_prompt(self, email: EmailRecord) -> str:
        """Craft the assistant prompt including allowed labels and email content."""
        label_lines = "\n".join([f'- "{item["name"]}": {item.get("description", "")}' for item in self.labels_config])
        return (
            "You are an email triage assistant. Choose exactly one label from the list below and respond with "
            "JSON: {\"label\": \"<label>\", \"confidence\": <0-1>}.\n"
            f"Labels:\n{label_lines}\n\n"
            f"Email subject: {email.subject}\nEmail body: {email.body}"
        )

    def _build_reviewer_prompt(self, email: EmailRecord, assistant_text: str) -> str:
        """Prompt the reviewer to validate or adjust the assistant's choice."""
        return (
            "You are reviewing an email classification. The assistant responded with the JSON below.\n"
            "If it is valid and uses allowed labels, confirm it. Otherwise, adjust to the best label.\n"
            f"Assistant output: {assistant_text}\n"
            f"Subject: {email.subject}\nBody: {email.body}\n"
            "Return JSON: {\"label\": \"<label>\", \"confidence\": <0-1>}."
        )

    def _parse_output(self, text: str) -> Dict[str, Any]:
        """Parse a JSON string or recover a label from raw text."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"label": self._normalize_label(text), "confidence": 0.5}

    def _normalize_label(self, raw_label: str) -> str:
        """Map arbitrary model output to a configured label."""
        normalized = raw_label.strip().lower()
        if normalized in self.label_names:
            return normalized
        return self.label_names[0] if self.label_names else normalized

    def _call_llm(self, prompt: str) -> Tuple[str, TokenUsage]:
        """Dispatch to Groq chat completions."""
        return self._call_groq(prompt)

    def _call_groq(self, prompt: str) -> Tuple[str, TokenUsage]:
        """Direct Groq chat completion call."""
        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        }
        attempts = 5
        backoff = 2.0
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                # Capture rate limiter sleep to separate actual runtime vs waiting.
                start_wait = time.perf_counter()
                self.rate_limiter.acquire()
                self.wait_seconds += max(time.perf_counter() - start_wait, 0.0)
                response = self.session.post(endpoint, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                text = ""
                try:
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
                except Exception:
                    text = ""
                usage_meta = data.get("usage", {})
                token_usage = TokenUsage(
                    prompt_tokens=int(usage_meta.get("prompt_tokens", max(len(prompt) // 4, 1))),
                    completion_tokens=int(usage_meta.get("completion_tokens", max(len(text) // 4, 1))),
                )
                return text, token_usage
            except Exception as error:
                last_error = error
                resp = getattr(error, "response", None)
                status = resp.status_code if resp is not None else None
                retry_after = 0.0
                if resp is not None:
                    try:
                        retry_after = float(resp.headers.get("Retry-After", 0.0))
                    except Exception:
                        retry_after = 0.0
                if status == 429:
                    time.sleep(max(retry_after, backoff))
                elif attempt < attempts:
                    time.sleep(backoff)
                if attempt < attempts:
                    backoff *= 2
                    continue
                raise RuntimeError(f"AutoGen Groq call failed: {error}") from error
        raise RuntimeError(f"AutoGen Groq call failed: {last_error}")  # safety

    def _estimate_usage(self, prompt: str, response: str) -> TokenUsage:
        """Approximate token usage when the provider omits token counts."""
        prompt_tokens = max(len(prompt) // 4, 1)
        completion_tokens = max(len(response) // 4, 1)
        return TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)

    def _combine_usage(self, first: TokenUsage, second: TokenUsage) -> TokenUsage:
        """Sum token usage across conversation turns."""
        return TokenUsage(
            prompt_tokens=first.prompt_tokens + second.prompt_tokens,
            completion_tokens=first.completion_tokens + second.completion_tokens,
        )

    def _invoke_assistant_and_reviewer(self, email: EmailRecord) -> Tuple[str, str, TokenUsage]:
        """Ensure both assistant and reviewer paths go through Groq at least once."""
        assistant_prompt = self._build_assistant_prompt(email)
        assistant_text, assistant_usage = self.assistant.propose(assistant_prompt, self._call_llm)
        review_prompt = self._build_reviewer_prompt(email, assistant_text)
        reviewer_text, reviewer_usage = self.reviewer.review(review_prompt, self._call_llm)
        total_usage = self._combine_usage(
            assistant_usage or self._estimate_usage(assistant_prompt, assistant_text),
            reviewer_usage or self._estimate_usage(review_prompt, reviewer_text),
        )
        return assistant_text, reviewer_text, total_usage
