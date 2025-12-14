"""Orchestrate running all pipelines on the dataset."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from common.io_utils import ensure_dir, get_project_root, load_yaml, write_json
from spl_runner.cli import main as spl_main
from langchain_runner.cli import main as lc_main
from autogen_runner.cli import main as ag_main


def _parse_methods(raw: str) -> List[str]:
    """Split and normalize the methods list supplied via CLI."""
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def main() -> None:
    """Run selected pipelines, ensuring dataset readiness, and index outputs."""
    parser = argparse.ArgumentParser(description="Run SPL vs baselines on the dataset.")
    parser.add_argument(
        "--methods",
        type=str,
        default="spl,langchain,autogen",
        help="Comma-separated list of methods to run.",
    )
    args = parser.parse_args()
    methods = _parse_methods(args.methods)

    run_paths: Dict[str, Path] = {}
    for method in methods:
        if method == "spl":
            run_paths["spl"] = spl_main()
        elif method == "langchain":
            run_paths["langchain"] = lc_main()
        elif method == "autogen":
            run_paths["autogen"] = ag_main()
        else:
            raise ValueError(f"Unknown method {method}")

    project_root = get_project_root()
    settings = load_yaml(project_root / "poc_config" / "settings.yaml")
    summary_dir = ensure_dir(project_root / settings["evaluation"]["summary_output_dir"])
    index_path = summary_dir / "latest_index.json"
    runs_payload = [
        {"method": method, "metrics_path": str(path / "metrics.json")}
        for method, path in run_paths.items()
    ]
    write_json(index_path, {"runs": runs_payload})
    print(f"Wrote latest index to {index_path}")


if __name__ == "__main__":
    main()
