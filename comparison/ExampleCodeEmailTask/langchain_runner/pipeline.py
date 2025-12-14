"""LangChain-style baseline using Groq chat completions without SPL state."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Tuple

import requests

from common.cost_model import estimate_cost_usd
from common.dataset import load_labels
from common.email_schema import ClassificationResult, EmailRecord, PerEmailMetrics, TokenUsage
from common.io_utils import load_yaml
from common.timing import RateLimiter, measure_latency_ms
from langchain_runner.prompts import build_system_prompt, build_user_prompt


class LangChainClassifier:
    """Simple one-shot classifier built on Groq HTTP."""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.providers = load_yaml(config_dir / "providers.yaml")
        self.labels_config = load_labels(config_dir)
        self.label_names = [item["name"] for item in self.labels_config]
        self.provider_label = "unknown"
        # Tracks how much wall time is spent waiting on client-side throttling/retries,
        # so we can report true runtime vs. wait time in metrics.
        self.wait_seconds = 0.0

        groq_cfg = self.providers.get("groq", {}).get("langchain", {})
        self.session = requests.Session()

        self.provider = "groq"
        self.model_name = groq_cfg.get("model") or groq_cfg.get("model_id") or "llama-3.1-8b-instant"
        self.api_key_env = groq_cfg.get("env_var", "GROQ_API_KEY")
        self.base_url = self.providers.get("groq", {}).get("base_url", "https://api.groq.com/openai/v1")
        self.provider_label = f"groq:{self.model_name}"
        if not self.api_key_env:
            raise ValueError("Missing env_var for LangChain client")
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise EnvironmentError(f"Environment variable {self.api_key_env} must be set")
        self.api_key = api_key

        rpm = int(groq_cfg.get("max_requests_per_minute") or 0)
        self.rate_limiter = RateLimiter(rpm)

    def classify(self, email: EmailRecord) -> Tuple[ClassificationResult, PerEmailMetrics]:
        """Classify a single email via one LLM call."""
        system_prompt = build_system_prompt(self.labels_config)
        user_prompt = build_user_prompt(email)
        prompt = f"{system_prompt}\n\n{user_prompt}"
        # Reset wait tracking per email to keep per-email metrics accurate.
        self.wait_seconds = 0.0
        with measure_latency_ms() as timer:
            parsed_text, token_usage = self._call_llm(prompt)
            parsed = self._parse_output(parsed_text)
            cost_usd = estimate_cost_usd(token_usage, self.model_name)

        latency_ms = timer.get("elapsed_ms", 0.0)
        wait_ms = self.wait_seconds * 1000.0
        actual_runtime_ms = max(latency_ms - wait_ms, 0.0)
        label = self._normalize_label(parsed.get("label", self.label_names[0] if self.label_names else ""))
        is_correct = label == email.true_label

        classification = ClassificationResult(
            email_id=email.id,
            predicted_label=label,
            method="langchain",
            raw_response={"text": parsed_text, "parsed": parsed, "from_llm": True},
        )
        metrics = PerEmailMetrics(
            email_id=email.id,
            true_label=email.true_label,
            predicted_label=label,
            method="langchain",
            latency_ms=latency_ms,
            wait_ms=wait_ms,
            actual_runtime_ms=actual_runtime_ms,
            token_usage=token_usage,
            cost_usd=cost_usd,
            layers_used=None,
            is_correct=is_correct,
        )
        return classification, metrics

    def _parse_output(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"label": self._normalize_label(text), "confidence": 0.5}

    def _normalize_label(self, raw_label: str) -> str:
        label = raw_label.strip().lower()
        if label in self.label_names:
            return label
        return self.label_names[0] if self.label_names else label

    def _call_llm(self, prompt: str) -> Tuple[str, TokenUsage]:
        return self._call_groq(prompt)

    def _call_groq(self, prompt: str) -> Tuple[str, TokenUsage]:
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
                # Rate limiter wait is counted toward wait_seconds for later reporting.
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
                raise RuntimeError(f"LangChain Groq call failed: {error}") from error
        raise RuntimeError(f"LangChain Groq call failed: {last_error}")  # safety

    def _estimate_usage(self, prompt: str, response: str) -> TokenUsage:
        prompt_tokens = max(len(prompt) // 4, 1)
        completion_tokens = max(len(response) // 4, 1)
        return TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
