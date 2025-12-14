"""Metrics aggregation for the LangChain baseline."""

from __future__ import annotations

from typing import List

from common.email_schema import PerEmailMetrics, RunMetrics
from common.evaluator import summarize_run


def build_langchain_run_metrics(per_email: List[PerEmailMetrics]) -> RunMetrics:
    """Summarize LangChain per-email metrics."""
    return summarize_run(per_email, method="langchain")
