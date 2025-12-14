"""AutoGen agent definitions for the baseline conversation."""

from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

from common.email_schema import TokenUsage


class EmailAssistantAgent:
    """Lightweight assistant that delegates to the provided LLM callable."""

    def __init__(self, provider: str):
        """Store provider name (Groq) for reference."""
        self.provider = provider

    def propose(self, prompt: str, fallback: Callable[[str], Tuple[str, TokenUsage]]) -> Tuple[str, TokenUsage]:
        """Generate a proposal using the provided fallback LLM caller."""
        return fallback(prompt)


class ReviewerAgent:
    """Lightweight reviewer that delegates to the provided LLM callable."""

    def __init__(self, provider: str):
        """Store provider name (Groq) for reference."""
        self.provider = provider

    def review(self, prompt: str, fallback: Callable[[str], Tuple[str, TokenUsage]]) -> Tuple[str, TokenUsage]:
        """Review the assistant output using the provided fallback LLM caller."""
        return fallback(prompt)
