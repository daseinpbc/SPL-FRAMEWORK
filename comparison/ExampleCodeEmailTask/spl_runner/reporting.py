"""Reporting utilities for SPL runs."""

from __future__ import annotations

from pathlib import Path
from typing import List

from common.email_schema import PerEmailMetrics, RunMetrics
from common.io_utils import ensure_dir, write_json, write_jsonl


def write_per_email(run_dir: Path, metrics: List[PerEmailMetrics]) -> Path:
    """Persist per-email metrics as JSONL."""
    ensure_dir(run_dir)
    path = run_dir / "per_email.jsonl"
    records = [m.model_dump() for m in metrics]
    write_jsonl(path, records)
    return path


def write_metrics(run_dir: Path, metrics: RunMetrics) -> Path:
    """Persist run-level metrics to JSON."""
    ensure_dir(run_dir)
    path = run_dir / "metrics.json"
    write_json(path, metrics.model_dump())
    return path


def write_explanation(run_dir: Path, metrics: RunMetrics) -> Path:
    """Write a human-readable summary of the SPL run."""
    ensure_dir(run_dir)
    path = run_dir / "explanation.md"
    layer_usage = metrics.extra.get("layer_usage", {})
    layer0 = int(layer_usage.get("layer0", 0))
    layer1 = int(layer_usage.get("layer1", 0))
    layer2 = int(layer_usage.get("layer2", 0))
    suppression_rate = layer_usage.get("suppression_rate", 0.0)
    l1_suppressed = int(metrics.extra.get("l1_suppressed_l2", 0))
    budget_remaining = metrics.extra.get("budget_remaining_final")
    tokens_used = metrics.extra.get("tokens_used_final")
    safety_total = int(metrics.extra.get("safety_violations_total", 0))
    content = (
        "# SPL run overview\n\n"
        "SPL applies three layers of control: Layer 0 validates inputs, "
        "Layer 1 uses learned patterns to short-circuit repeated cases, "
        "and Layer 2 calls Gemini only when the earlier layers cannot decide.\n\n"
        "Key observations for this run:\n"
        f"- Emails finalized by Layer 0: {layer0}\n"
        f"- Emails finalized by Layer 1: {layer1} (patterns suppressed L2: {l1_suppressed})\n"
        f"- Emails requiring Layer 2 (Gemini): {layer2}\n"
        f"- Suppression rate (Layer 2 avoided): {suppression_rate:.2%}\n"
        f"- Accuracy: {metrics.accuracy:.2%}\n"
        f"- Average latency (ms): {metrics.avg_latency_ms:.2f}\n"
        f"- Average cost per email (USD): {metrics.avg_cost_usd_per_email:.6f}\n"
        f"- Final budget remaining (USD): {budget_remaining}\n"
        f"- Total tokens used: {tokens_used}\n"
        f"- Safety violations recorded: {safety_total}\n\n"
        "Lower layers reuse world state and learned patterns, so later emails can skip "
        "expensive model calls while keeping accuracy high."
    )
    path.write_text(content, encoding="utf-8")
    return path
