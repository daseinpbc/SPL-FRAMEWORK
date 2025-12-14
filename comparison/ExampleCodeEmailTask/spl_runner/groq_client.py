"""Groq MCP client that calls the Groq chat completions API."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import requests

from common.timing import RateLimiter
from spl.mcp_integration import MCPClient, MCPResponse


class GroqMCPClient(MCPClient):
    """MCP client implementation for Groq's OpenAI-compatible chat endpoint."""

    def __init__(
        self,
        model: str,
        api_token: str,
        base_url: str = "https://api.groq.com/openai/v1",
        rate_limiter: Optional[RateLimiter] = None,
    ):
        # Provide a non-None api_client so MCPClient.reason delegates to _call_api.
        super().__init__(model=model, api_client=True, cost_per_call=0.0)
        self.model = model
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.rate_limiter = rate_limiter
        # Expose wait timing so callers can subtract throttling time from runtime metrics.
        self.last_wait_seconds: float = 0.0
        self.total_wait_seconds: float = 0.0

    def _call_api(self, content: str, context: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """Call Groq chat completions and return an MCPResponse."""
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0.0,
        }
        if context:
            payload.update(context)

        attempts = 5
        backoff = 2.0
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                wait_start = time.perf_counter()
                if self.rate_limiter:
                    self.rate_limiter.acquire()
                    waited = max(time.perf_counter() - wait_start, 0.0)
                    self.last_wait_seconds = waited
                    self.total_wait_seconds += waited
                else:
                    self.last_wait_seconds = 0.0
                response = self.session.post(endpoint, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                message_text = ""
                try:
                    message_text = data.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
                except Exception:
                    message_text = ""

                category, confidence = self._extract_classification(message_text)

                return MCPResponse(
                    content=message_text,
                    category=category,
                    confidence=confidence,
                    cost=self.cost_per_call,
                    model=self.model,
                )
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
                raise
        raise last_error or RuntimeError("Groq call failed")

    def _extract_classification(self, text: str) -> tuple[str, float]:
        """Parse label/confidence from Groq response text."""
        if not text:
            return "other", 0.0
        try:
            parsed = json.loads(text)
            label = str(parsed.get("label", "other")).strip().lower()
            confidence = float(parsed.get("confidence", 0.0))
            return label or "other", confidence
        except Exception:
            words = text.strip().split()
            return (words[0].lower() if words else "other"), 0.0
