"""Reporting helpers for the AutoGen baseline."""

from __future__ import annotations

from pathlib import Path
from typing import List

from common.email_schema import PerEmailMetrics, RunMetrics
from common.io_utils import ensure_dir, write_json, write_jsonl


def write_per_email(run_dir: Path, metrics: List[PerEmailMetrics]) -> Path:
    """Persist per-email metrics as JSONL."""
    ensure_dir(run_dir)
    path = run_dir / "per_email.jsonl"
    write_jsonl(path, [m.model_dump() for m in metrics])
    return path


def write_metrics(run_dir: Path, metrics: RunMetrics) -> Path:
    """Persist run-level metrics."""
    ensure_dir(run_dir)
    path = run_dir / "metrics.json"
    write_json(path, metrics.model_dump())
    return path


def write_explanation(run_dir: Path, metrics: RunMetrics) -> Path:
    """Write a short Markdown note describing the AutoGen run."""
    ensure_dir(run_dir)
    path = run_dir / "explanation.md"
    content = (
        "# AutoGen baseline\n\n"
        "Two lightweight agents collaborate: one proposes a label and another reviews it. "
        "There is no shared world state or suppression logic; each email triggers a short conversation.\n\n"
        f"- Accuracy: {metrics.accuracy:.2%}\n"
        f"- Average latency (ms): {metrics.avg_latency_ms:.2f}\n"
        f"- Average cost per email (USD): {metrics.avg_cost_usd_per_email:.6f}\n"
        "Because both agents can call the model, token usage is typically higher than the SPL layered approach."
    )
    path.write_text(content, encoding="utf-8")
    return path
