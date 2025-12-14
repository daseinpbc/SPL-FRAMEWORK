"""Command-line entrypoint for running the SPL pipeline over the dataset."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import List

from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common.dataset import generate_synthetic_emails, load_email_dataset, save_email_dataset
from common.email_schema import PerEmailMetrics
from common.io_utils import get_project_root, load_yaml, ensure_dir
from spl_runner.metrics import build_spl_run_metrics
from spl_runner.pipeline import SPLClassifier
from spl_runner.reporting import write_explanation, write_metrics, write_per_email


def _ensure_dataset(config_dir: Path) -> Path:
    """Generate the synthetic dataset if it does not yet exist."""
    settings = load_yaml(config_dir / "settings.yaml")
    dataset_cfg = settings.get("dataset", {})
    labels_path = config_dir / "labels.yaml"
    settings_path = config_dir / "settings.yaml"
    dataset_path = get_project_root() / dataset_cfg.get("output_path", "data/processed/emails_1000.jsonl")
    if dataset_path.exists():
        return dataset_path

    emails = generate_synthetic_emails(settings_path, labels_path)
    save_email_dataset(dataset_path, emails)
    return dataset_path


def main() -> Path:
    """Run the SPL classifier across the full dataset."""
    project_root = get_project_root()
    config_dir = project_root / "poc_config"
    settings = load_yaml(config_dir / "settings.yaml")
    dataset_path = _ensure_dataset(config_dir)
    emails = load_email_dataset(dataset_path)

    classifier = SPLClassifier(config_dir=config_dir)
    per_email_metrics: List[PerEmailMetrics] = []

    print(f"[SPL] Using provider: {classifier.provider}")

    for email in tqdm(emails, desc="SPL classifying"):
        _, metrics = classifier.classify(email)
        per_email_metrics.append(metrics)

    run_metrics = build_spl_run_metrics(per_email_metrics)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_root = project_root / settings["evaluation"]["metrics_output_dir"] / f"spl_run_{timestamp}"
    ensure_dir(run_root)

    write_per_email(run_root, per_email_metrics)
    write_metrics(run_root, run_metrics)
    write_explanation(run_root, run_metrics)

    print(
        f"SPL run complete: accuracy={run_metrics.accuracy:.2%}, "
        f"avg latency={run_metrics.avg_latency_ms:.1f} ms, "
        f"avg cost/email=${run_metrics.avg_cost_usd_per_email:.6f}"
    )
    return run_root


if __name__ == "__main__":
    main()
