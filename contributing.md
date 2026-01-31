# Contributing to SPL Framework

Thank you for your interest in contributing to the Subsumption Pattern Learning (SPL) Framework.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Redis (for multi-agent shared state)

### Setup

```bash
git clone https://github.com/daseinpbc/SPL-FRAMEWORK.git
cd SPL-FRAMEWORK
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=spl/

# Run specific test file
pytest tests/test_layer1.py -v
```

---

## Project Structure

```
spl/
├── agent.py                 # SPL Agent orchestrator (Definition 1)
├── layer0_reactive.py       # Structural validation (Definition 2)
├── layer1_tactical.py       # Pattern matching + inhibition (Definitions 3, 5)
├── layer2_deliberative.py   # Foundation model + distillation (Definition 4, 8)
├── cost_tracker.py          # Cost monitoring
└── mcp_integration.py       # MCP client support

tests/                       # Test suite
examples/                    # Usage examples
comparison/                  # Benchmark suite
docs/                        # Documentation
```

---

## How to Contribute

### Reporting Issues

- Use the [GitHub Issue Tracker](https://github.com/daseinpbc/SPL-FRAMEWORK/issues)
- Include reproduction steps and expected vs. actual behavior

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Ensure tests pass: `pytest tests/`
5. Submit a pull request

### Code Style

- Follow PEP 8
- Use type hints where possible
- Keep functions focused and well-named

---

## Good First Issues

- Implement additional pattern types (semantic embeddings beyond regex)
- Add support for new foundation model providers via MCP
- Benchmark on additional datasets
- Improve test coverage for edge cases

---

## Areas of Active Development

Based on the paper's Future Work (Section 8):

1. **Automated Pattern Distillation** (Section 8.1): Train distillation models that extract patterns from reasoning traces, implement in-context learning for few-shot pattern induction
2. **Adaptive Threshold Learning** (Section 8.2): Learn theta and alpha from observed accuracy-cost tradeoffs rather than using fixed values
3. **Cross-Domain Transfer** (Section 8.3): Evaluate pattern transfer across related domains, study emergent specialization in heterogeneous swarms
4. **Large-Scale Deployment** (Section 8.4): Test with 100+ agents, study Shared State synchronization overhead and pattern library scaling

---

## Key Concepts for Contributors

Understanding these paper concepts will help when contributing:

- **Pattern**: A tuple `p = (phi_p, psi_p, kappa_p)` -- matcher, responder, complexity bound
- **Inhibition Signal**: `I_1(x) = true` when pattern confidence exceeds theta and complexity is below alpha
- **Suppression Rate (rho)**: Fraction of requests resolved without Layer 2
- **Pattern Distillation**: Extracting reusable patterns from Layer 2 reasoning traces
- **Stigmergic Reinforcement**: Confidence scores grow on success, decay on failure -- like pheromone trails
- **Shared State**: Collective memory `S = (P_shared, C, M, A)` enabling cross-agent learning

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full formal framework.

---

## Contact

**Author:** Pamela Cuce -- pamela.cuce@tufts.edu
