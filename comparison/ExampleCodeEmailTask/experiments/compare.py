"""Generate comparison charts across SPL and baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from common.email_schema import RunMetrics
from common.io_utils import ensure_dir, get_project_root, load_yaml
from common.plotting import (
    plot_accuracy_vs_method,
    plot_cost_vs_method,
    plot_latency_vs_method,
    plot_spl_layer_usage,
    plot_tokens_vs_method,
)


def _load_runs(latest_index: Path) -> List[RunMetrics]:
    """Load RunMetrics objects for all runs referenced by the index."""
    data = json.loads(latest_index.read_text(encoding="utf-8"))
    project_root = get_project_root()
    metrics: List[RunMetrics] = []
    for run in data.get("runs", []):
        metrics_path = project_root / run["metrics_path"]
        metrics_data = json.loads(metrics_path.read_text(encoding="utf-8"))
        metrics.append(RunMetrics.model_validate(metrics_data))
    return metrics


def main() -> None:
    """Render comparison charts for latency, cost, tokens, accuracy, and SPL layers."""
    project_root = get_project_root()
    settings = load_yaml(project_root / "poc_config" / "settings.yaml")
    summary_dir = project_root / settings["evaluation"]["summary_output_dir"]
    latest_index = summary_dir / "latest_index.json"
    if not latest_index.exists():
        raise FileNotFoundError("latest_index.json not found. Run experiments.run_all first.")

    run_metrics = _load_runs(latest_index)
    charts_dir = ensure_dir(project_root / settings["plotting"]["charts_dir"])

    plot_latency_vs_method(run_metrics, charts_dir)
    plot_cost_vs_method(run_metrics, charts_dir)
    plot_tokens_vs_method(run_metrics, charts_dir)
    plot_accuracy_vs_method(run_metrics, charts_dir)
    plot_spl_layer_usage(run_metrics, charts_dir)

    for metric in run_metrics:
        print(
            f"{metric.method}: accuracy={metric.accuracy:.2%}, "
            f"latency={metric.avg_latency_ms:.1f} ms, "
            f"cost/email=${metric.avg_cost_usd_per_email:.6f}"
        )
    print(f"Charts written to {charts_dir}")


if __name__ == "__main__":
    main()
