"""Metrics aggregation for the AutoGen baseline."""

from __future__ import annotations

from typing import List

from common.email_schema import PerEmailMetrics, RunMetrics
from common.evaluator import summarize_run


def build_autogen_run_metrics(per_email: List[PerEmailMetrics]) -> RunMetrics:
    """Summarize AutoGen per-email metrics."""
    return summarize_run(per_email, method="autogen")
