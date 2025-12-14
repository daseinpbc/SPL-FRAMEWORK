"""Reporting helpers for the LangChain baseline."""

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
    """Persist run-level metrics to JSON."""
    ensure_dir(run_dir)
    path = run_dir / "metrics.json"
    write_json(path, metrics.model_dump())
    return path


def write_explanation(run_dir: Path, metrics: RunMetrics) -> Path:
    """Write a short Markdown explanation of the baseline approach."""
    ensure_dir(run_dir)
    path = run_dir / "explanation.md"
    content = (
        "# LangChain baseline\n\n"
        "This baseline sends each email directly to a Groq chat model via LangChain without\n"
        "state sharing or suppression. Every email invokes the LLM independently.\n\n"
        f"- Accuracy: {metrics.accuracy:.2%}\n"
        f"- Average latency (ms): {metrics.avg_latency_ms:.2f}\n"
        f"- Average cost per email (USD): {metrics.avg_cost_usd_per_email:.6f}\n"
        "Because there is no pattern learning across emails, token and cost scales linearly with the dataset size."
    )
    path.write_text(content, encoding="utf-8")
    return path
