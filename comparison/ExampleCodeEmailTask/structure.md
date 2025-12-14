# Project Structure (Simple Overview)

Plain-language map of what lives where in this POC.

## Top-Level
- `POC/` — The runnable email-classification POC (this file lives here).
- `SPL-FRAMEWORK/` — The upstream SPL library (layers, MCP client abstractions).

## POC Contents
- `common/` — Shared schemas, cost model, plotting, timing helpers.
- `poc_config/` — Settings, labels, provider config (e.g., Groq model + RPM, pricing).
- `spl_runner/` — SPL MCP orchestrator, Groq client, CLI entrypoint, metrics/reporting.
- `spl_mcp/` — Local MCP servers for reactive (L0), tactical (L1), deliberative (L2) layers.
- `langchain_runner/` — Baseline: single Groq call per email (no SPL suppression).
- `autogen_runner/` — Baseline: AutoGen assistant+reviewer flow using Groq.
- `experiments/` — Utilities to run all methods and build summaries/charts.
- `results/` — Run outputs (`results/runs/...`) and aggregated summaries (`results/summary/...`).
- `tests/` — Unit tests (lightweight).
- `scripts/` — Helper scripts (if present).

## Key Config Files
- `poc_config/providers.yaml` — Provider endpoints, model IDs, RPM, pricing.
- `poc_config/settings.yaml` — Dataset and evaluation knobs (output dirs, sizes, thresholds).
- `poc_config/labels.yaml` — Label set and descriptions.

## Entry Points
- `python spl_runner/cli.py` — Full SPL pipeline (L0→L1→L2 via MCP, Groq L2).
- `python langchain_runner/cli.py` — Baseline single-call classifier.
- `python autogen_runner/cli.py` — Baseline AutoGen conversation.
- `python -m experiments.run_all` — Run SPL + baselines and index outputs.
- `python -m experiments.summarize` — Build comparison JSON/MD from the latest index.
- `python -m experiments.compare` — Generate charts and summaries from indexed runs.

## Results Layout
- `results/runs/<method>_run_<timestamp>/` — `per_email.jsonl`, `metrics.json`, `explanation.md`.
- `results/summary/` — `latest_index.json`, `comparison.json`, `comparison.md`, charts.

## External Dependency
- Groq LLM: set `GROQ_API_KEY` and ensure the configured model (default `llama-3.1-8b-instant`) is available.
