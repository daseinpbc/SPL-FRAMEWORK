# Run Guide (macOS, Linux, WSL2)

Applies to the POC in `POC/` with Groq (`llama-3.1-8b-instant`) as the L2 model.

## Prereqs
- Python 3.11+
- Groq API key: `export GROQ_API_KEY="your_key"`

## Setup
```bash
cd POC
python3 -m venv .venv
source .venv/bin/activate   # Windows/WSL2: source .venv/bin/activate
pip install -e .
```

## Run a Single Pipeline
- SPL (MCP L0→L1→L2): `python spl_runner/cli.py`
- LangChain baseline: `python langchain_runner/cli.py`
- AutoGen baseline: `python autogen_runner/cli.py`

Outputs land in `results/runs/<method>_run_<timestamp>/`.

## Run Everything + Summaries
```bash
python -m experiments.run_all          # runs spl, langchain, autogen and writes latest_index.json
python -m experiments.summarize        # builds comparison.json/comparison.md
python -m experiments.compare          # generates charts under results/summary/charts
```

## Notes
- Rate limits: Groq RPM is set in `poc_config/providers.yaml` (default 29). Runs may pause for throttling; metrics include wait time.
- Dataset: auto-generated to `data/processed/emails_1000.jsonl` if missing.
- If `experiments.summarize` complains about `latest_index.json`, rerun `experiments.run_all` or update `results/summary/latest_index.json` to point at your latest `metrics.json` files.
