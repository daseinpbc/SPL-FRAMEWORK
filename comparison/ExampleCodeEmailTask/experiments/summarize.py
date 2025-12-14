"""Summarize recent runs into comparison artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from common.email_schema import RunMetrics
from common.io_utils import get_project_root, write_json
from common.io_utils import load_yaml as load_yaml_file
import json


def _load_latest_index(summary_dir: Path) -> Dict:
    """Read the latest_index.json file to locate recent runs."""
    index_path = summary_dir / "latest_index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"{index_path} does not exist. Run experiments.run_all first.")
    return json.loads(index_path.read_text(encoding="utf-8"))


def _load_metrics(metrics_path: Path) -> RunMetrics:
    """Load a RunMetrics instance from a metrics.json file."""
    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    return RunMetrics.model_validate(data)


def _relative_stats(metrics: RunMetrics, baseline: Optional[RunMetrics]) -> Dict[str, float]:
    """Compute ratios against a baseline (LangChain) run for cost/latency/tokens."""
    if baseline is None:
        return {}
    cost_ratio = (
        metrics.avg_cost_usd_per_email / baseline.avg_cost_usd_per_email
        if baseline.avg_cost_usd_per_email
        else 0.0
    )
    latency_ratio = (
        metrics.avg_latency_ms / baseline.avg_latency_ms if baseline.avg_latency_ms else 0.0
    )
    baseline_tokens = baseline.total_prompt_tokens + baseline.total_completion_tokens
    tokens = metrics.total_prompt_tokens + metrics.total_completion_tokens
    token_savings = 0.0
    if baseline_tokens:
        token_savings = 1 - (tokens / baseline_tokens)
    return {
        "cost_ratio_vs_langchain": cost_ratio,
        "latency_ratio_vs_langchain": latency_ratio,
        "token_savings_vs_langchain": token_savings,
    }


def main() -> None:
    """Build JSON and Markdown comparisons from the most recent runs."""
    project_root = get_project_root()
    settings = load_yaml_file(project_root / "poc_config" / "settings.yaml")
    summary_dir = project_root / settings["evaluation"]["summary_output_dir"]
    comparison_path = summary_dir / "comparison.json"
    md_path = summary_dir / "comparison.md"

    index = _load_latest_index(summary_dir)
    runs = index.get("runs", [])
    run_metrics: List[RunMetrics] = []
    for run in runs:
        metrics_path = project_root / run["metrics_path"]
        run_metrics.append(_load_metrics(metrics_path))

    langchain_metrics = next((m for m in run_metrics if m.method == "langchain"), None)
    comparison_payload = []
    for metrics in run_metrics:
        comparison_payload.append(
            {
                "method": metrics.method,
                "metrics": metrics.model_dump(),
                "relative": _relative_stats(metrics, langchain_metrics),
            }
        )
    write_json(comparison_path, comparison_payload)

    # Markdown summary
    lines = [
        "# Method comparison",
        "This report compares SPL's layered approach with two baselines that call Gemini directly.",
        "",
    ]
    for entry in comparison_payload:
        method = entry["method"]
        m = next((rm for rm in run_metrics if rm.method == method), None)
        if not m:
            continue
        rel = entry["relative"]
        lines.append(f"## {method.title()}")
        lines.append(f"- Accuracy: {m.accuracy:.2%}")
        lines.append(f"- Avg latency (ms): {m.avg_latency_ms:.1f}")
        lines.append(f"- Avg cost/email (USD): {m.avg_cost_usd_per_email:.6f}")
        if rel:
            lines.append(f"- Cost vs LangChain: {rel['cost_ratio_vs_langchain']:.2f}x")
            lines.append(f"- Latency vs LangChain: {rel['latency_ratio_vs_langchain']:.2f}x")
            lines.append(
                f"- Token savings vs LangChain: {rel['token_savings_vs_langchain']:.2%}"
            )
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {comparison_path} and {md_path}")


if __name__ == "__main__":
    main()
