"""Lightweight sanity tests for dataset generation and loading."""

from pathlib import Path

from common.dataset import generate_synthetic_emails, load_email_dataset, save_email_dataset


def test_generate_and_load_tiny_dataset(tmp_path: Path) -> None:
    """Generate a tiny dataset and ensure roundtrip save/load works."""
    settings = Path("poc_config/settings.yaml")
    labels = Path("poc_config/labels.yaml")
    # Override output path
    out_path = tmp_path / "emails_test.jsonl"
    emails = generate_synthetic_emails(settings, labels)
    # Take a small subset for speed
    emails_small = emails[:10]
    save_email_dataset(out_path, emails_small)
    loaded = load_email_dataset(out_path)
    assert len(loaded) == len(emails_small)
    assert all(e.true_label for e in loaded)
