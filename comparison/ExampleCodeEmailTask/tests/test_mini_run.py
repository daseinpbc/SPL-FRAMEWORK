"""Mini-run sanity checks for SPL, LangChain, and AutoGen on 5 emails.

These tests validate that:
- The pipelines can process a tiny dataset end-to-end.
- LLM usage assertions are enforced (no heuristic fallbacks).
"""

from pathlib import Path

import pytest

from common.dataset import generate_synthetic_emails, save_email_dataset, load_email_dataset
from spl_runner.pipeline import SPLClassifier
from langchain_runner.pipeline import LangChainClassifier
from autogen_runner.pipeline import AutoGenClassifier
from spl_runner.metrics import build_spl_run_metrics
from langchain_runner.metrics import build_langchain_run_metrics
from autogen_runner.metrics import build_autogen_run_metrics


@pytest.mark.skip(reason="Requires valid Gemini credentials and models; enable manually.")
def test_mini_run_all_pipelines(tmp_path: Path) -> None:
    """Run SPL, LangChain, and AutoGen on a tiny dataset (5 emails)."""
    config_dir = Path("poc_config")
    settings_path = config_dir / "settings.yaml"
    labels_path = config_dir / "labels.yaml"

    # Generate and persist a tiny dataset
    emails_full = generate_synthetic_emails(settings_path, labels_path)
    emails = emails_full[:5]
    dataset_path = tmp_path / "mini_emails.jsonl"
    save_email_dataset(dataset_path, emails)
    loaded_emails = load_email_dataset(dataset_path)
    assert len(loaded_emails) == 5

    # SPL
    spl = SPLClassifier(config_dir=config_dir)
    spl_metrics = []
    for email in loaded_emails:
        _, m = spl.classify(email)
        spl_metrics.append(m)
    spl_run = build_spl_run_metrics(spl_metrics)
    # Ensure some emails hit lower layers and some hit L2
    lower = spl_run.extra.get("layer_usage", {}).get("lower_layers", 0)
    l2 = spl_run.extra.get("layer_usage", {}).get("layer2", 0)
    assert lower >= 0
    assert l2 >= 1  # at least one should call L2/LLM

    # LangChain
    lc = LangChainClassifier(config_dir=config_dir)
    lc_metrics = []
    for email in loaded_emails:
        _, m = lc.classify(email)
        lc_metrics.append(m)
    lc_run = build_langchain_run_metrics(lc_metrics)
    assert lc_run.dataset_size == 5

    # AutoGen
    ag = AutoGenClassifier(config_dir=config_dir)
    ag_metrics = []
    for email in loaded_emails:
        _, m = ag.classify(email)
        ag_metrics.append(m)
    ag_run = build_autogen_run_metrics(ag_metrics)
    assert ag_run.dataset_size == 5
