"""SPL-specific metric aggregation helpers."""

from __future__ import annotations

from typing import Dict, List

from common.email_schema import PerEmailMetrics, RunMetrics
from common.evaluator import summarize_run


def build_spl_run_metrics(per_email: List[PerEmailMetrics]) -> RunMetrics:
    """Aggregate metrics and annotate SPL layer usage details."""
    run_metrics = summarize_run(per_email, method="spl")
    l0_final = sum(1 for m in per_email if m.final_layer == "L0")
    l1_final = sum(1 for m in per_email if m.final_layer == "L1")
    layer2_calls = sum(1 for m in per_email if m.final_layer == "L2")
    l1_suppressed = sum(1 for m in per_email if m.l1_suppressed_l2)
    total = len(per_email)
    total_violations = sum(len(m.safety_violations or []) for m in per_email)
    layer_usage: Dict[str, float | int] = {
        "layer0": l0_final,
        "layer1": l1_final,
        "layer2": layer2_calls,
        "suppression_rate": (l1_suppressed / total) if total else 0.0,
    }
    run_metrics.extra["layer_usage"] = layer_usage
    run_metrics.extra["l1_suppressed_l2"] = l1_suppressed
    run_metrics.extra["budget_remaining_final"] = per_email[-1].budget_remaining if per_email else None
    run_metrics.extra["tokens_used_final"] = per_email[-1].tokens_used if per_email else 0
    run_metrics.extra["safety_violations_total"] = total_violations
    return run_metrics
