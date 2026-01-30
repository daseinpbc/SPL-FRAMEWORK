# Subsumption Pattern Learning (SPL) Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Compliant-brightgreen.svg)](https://modelcontextprotocol.io/)
[![arXiv](https://img.shields.io/badge/arXiv-2501.XXXXX-b31b1b.svg)](https://arxiv.org/abs/2501.XXXXX)
[![Cost Reduction: 13.9x](https://img.shields.io/badge/Cost%20Reduction-13.9x-success.svg)](#experimental-results)

**A hierarchical multi-agent framework that transforms collections of autonomous AI agents into a self-distilling swarm intelligence through shared collective memory.**

SPL adapts Brooks' subsumption architecture from behavioral robotics to foundation model economics, implementing a formally-defined three-layer hierarchy (Reactive, Tactical, Deliberative) where learned patterns are distilled into a centralized Shared State via explicit inhibition signals.

> **Paper:** *Subsumption Pattern Learning: A Formal Framework for Self-Distilling Swarm Intelligence Through Shared Collective Memory* (Cuce, 2026)

---

## 📊 Key Results

| Metric | SPL | vs. Monolithic LLM | vs. FrugalGPT |
|--------|-----|-------------------|---------------|
| **Cost (100K tasks)** | $89.47 | **13.9× reduction** | **3.2× reduction** |
| **Latency (median)** | 7ms | **22× faster** | 4× faster |
| **Accuracy** | 96.9% | -1.3% | -0.5% |
| **Suppression Rate** | 94.5% | — | — |

*Multi-agent swarm learning achieves an additional **42% reduction** in foundation model escalations.*

---

## 🎯 The Isolated Agent Problem

Modern LLM-based agents operate as isolated computational units, each invoking expensive foundation models independently without mechanisms for inter-agent learning or knowledge reuse. This isolation contradicts four decades of insights from behavioral robotics, swarm biology, and organizational psychology.

**The economic consequences are significant:**
- Reasoning models generate 5× more tokens per request
- Multi-step agentic workflows compound costs further
- Daily costs can reach thousands of dollars
- Costs remain constant even as agents repeatedly solve nearly identical problems

---

## ✨ The SPL Solution

SPL unifies three previously disparate research streams:

1. **Subsumption Architecture** (Brooks, 1986): Layered behavioral control where simpler reactive modules suppress more complex deliberative ones
2. **Social Learning Theory** (Bandura, 1977): Collectives outperform individuals when knowledge is effectively shared
3. **Swarm Intelligence** (Kennedy & Eberhart, 2001): Decentralized systems with shared environmental state solve optimization problems through local interactions

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Incoming Request x                          │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 0: Reactive / Structural Validation                      │
│  ─────────────────────────────────────────                      │
│  L₀(x) = (ERROR, e) if ¬valid(x), else (PASS, x)               │
│  Cost: $0  |  Latency: <1ms  |  Deterministic checks            │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓ I₀ = false
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: Tactical / Pattern Matching                           │
│  ─────────────────────────────────────                          │
│  L₁(x) = (MATCH, ψ_p*(x)) if ∃p*: φ_p*(x) ≥ θ ∧ complexity(x) ≤ α│
│  Cost: ~$0.0001  |  Latency: <10ms  |  Pattern library lookup   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Inhibition Signal: I₁(x) = true → SUPPRESS Layer 2      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓ I₁ = false (escalate)
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: Deliberative / Foundation Model Reasoning             │
│  ─────────────────────────────────────────────────              │
│  L₂(x) = (SOLVED, L(x), distill(L, x))                         │
│  Cost: $0.01-$0.10  |  Latency: 100-500ms  |  LLM inference     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Pattern Distillation: New patterns → Shared State       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Formal Framework

### Definition 1: SPL Agent

An SPL agent is a tuple **A = (P_local, S, θ, α, L)** where:

- **P_local**: Agent's local pattern set
- **S**: Reference to the shared collective memory
- **θ ∈ (0, 1)**: Confidence threshold for Layer 1 suppression
- **α ∈ ℝ⁺**: Complexity threshold
- **L : X → Y**: Layer 2 foundation model

### Definition 2: Pattern

A pattern **p = (φ_p, ψ_p, κ_p)** consists of:

- **φ_p : X → [0, 1]**: Matcher returning match confidence
- **ψ_p : X → Y**: Responder producing outputs for matched inputs
- **κ_p ∈ ℝ⁺**: Complexity bound

### Definition 3: Inhibition Signal

The Layer 1 inhibition signal **I₁ : X → {true, false}**:

```
I₁(x) = true   if max_{p∈P_e} φ_p(x) ≥ θ ∧ complexity(x) ≤ α
        false  otherwise
```

When **I₁(x) = true**, Layer 2 execution is **suppressed**.

### Definition 4: Suppression Rate

```
ρ = |{x ∈ X_test : I₁(x) = true}| / |X_test|
```

---

## 📦 Shared State Protocol

The Shared State **S** serves as the swarm's collective memory, enabling stigmergic coordination across agents.

### Structure

**S = (P_shared, C, M, A)** where:

- **P_shared**: Global pattern library
- **C : P_shared → [0, 1]**: Pattern → confidence scores
- **M : P_shared → ℕ**: Pattern → match counts (reinforcement)
- **A : P_shared → AgentID**: Pattern provenance tracking

### Confidence Update Rules

**Reinforcement** (successful match):
```
C'(p) = C(p) + η(1 - C(p))
```

**Decay** (incorrect response):
```
C'(p) = C(p) · (1 - δ)
```

This implements **stigmergic reinforcement**: successful patterns accumulate confidence like pheromone trails, while failed patterns decay.

### Multi-Agent Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Agent A   │     │   Agent B   │     │   Agent C   │
├─────────────┤     ├─────────────┤     ├─────────────┤
│  Layer 0    │     │  Layer 0    │     │  Layer 0    │
│  Layer 1    │     │  Layer 1    │     │  Layer 1    │
│  Layer 2    │     │  Layer 2    │     │  Layer 2    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │ Write              │ Read/Write        │ Write
       ↓                    ↓                   ↓
┌─────────────────────────────────────────────────────┐
│              SHARED STATE (Collective Memory)        │
├─────────────────────────────────────────────────────┤
│  Learned Patterns  │  Confidence  │  Cross-Agent    │
│  P_shared          │  Scores C(p) │  Markers M(p)   │
└─────────────────────────────────────────────────────┘
                           ↓
              Emergent Swarm Intelligence
```

---

## 📈 Intelligence Compounding Theory

### Theorem (Intelligence Compounding)

Under mild assumptions, collective competency satisfies:

```
Γ(n) = 1 - e^(-πμn/k)
```

where:
- **n**: Number of processed requests
- **π**: Probability a novel input yields a distillable pattern
- **μ**: Measure of input space covered by each pattern
- **k**: Coverage constant

### Corollary (Logarithmic Learning)

To achieve competency Γ*, the swarm requires:

```
n* = (k/πμ) · ln(1/(1 - Γ*))
```

**Key insight:** Multi-agent systems amplify this effect—if *m* agents share state, the effective rate is *m · π*, reducing time to competency by factor *m*.

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/daseinpbc/SPL-FRAMEWORK.git
cd SPL-FRAMEWORK

# Install dependencies
pip install -r requirements.txt

# For multi-agent shared state
pip install redis
```

### Basic Usage

```python
from spl import SPLAgent

# Initialize agent with formal parameters
agent = SPLAgent(
    theta=0.87,      # Confidence threshold (θ)
    alpha=0.6,       # Complexity threshold (α)
    eta=0.1,         # Learning rate (η)
    delta=0.05       # Decay rate (δ)
)

# Add patterns to Layer 1 (P_local)
agent.layer1.add_pattern(
    name='urgent',
    matcher=r'urgent|asap|emergency',  # φ_p
    responder='urgent',                 # ψ_p
    confidence=0.95                     # Initial C(p)
)

# Process request
result = agent.process({
    'user_id': 'user123',
    'content': 'URGENT: Server outage in production'
})

print(result)
# {
#   'result': 'urgent',
#   'layer': 1,                    # Handled by Layer 1
#   'cost': 0.0001,
#   'confidence': 0.95,
#   'inhibition': True,            # I₁(x) = true
#   'suppressed_layer2': True      # Layer 2 NOT invoked
# }
```

### Multi-Agent Swarm Configuration

```python
from spl import SPLAgent, SharedState
import redis

# Initialize shared state (collective memory)
redis_client = redis.Redis(host='localhost', port=6379)
shared_state = SharedState(
    client=redis_client,
    theta_inherit=0.75,    # Inheritance threshold
    sync_interval=100      # ms
)

# Create swarm of agents sharing state
agents = [
    SPLAgent(shared_state=shared_state, agent_id=f'agent_{i}')
    for i in range(5)
]

# When Agent A learns a pattern...
agents[0].process({'content': 'Complex query requiring Layer 2...'})

# ...Agents B-E automatically inherit it via Shared State
# Future similar queries resolved at Layer 1 (zero FM cost)
```

### MCP Integration (Foundation Model Agnostic)

```python
from spl import SPLAgent
from spl.mcp_integration import MCPClient
import anthropic

# Layer 2 can use any foundation model via MCP
client = anthropic.Anthropic()
layer2_mcp = MCPClient(
    model="claude-sonnet-4-20250514",
    api_client=client,
)

agent = SPLAgent()
agent.layer2 = layer2_mcp

# Automatic pattern distillation from Layer 2 responses
result = agent.process({
    'content': 'Novel query requiring deliberative reasoning...'
})
# New pattern extracted and added to Shared State
```

---

## 📊 Experimental Results

### Benchmark: 100,000 Heterogeneous Enterprise Tasks

Dataset composition:
- Email Classification: 40,000 tasks
- Customer Inquiry Resolution: 35,000 tasks  
- Data Pipeline Orchestration: 25,000 tasks

### Single-Agent Performance

| System | Cost (USD) | Latency (ms) | Accuracy | Suppression Rate |
|--------|-----------|--------------|----------|------------------|
| Monolithic LLM | $1,247.32 | 847 ± 312 | 98.2% | 0.0% |
| FrugalGPT | $312.18 | 523 ± 287 | 97.4% | — |
| RouteLLM | $287.45 | 498 ± 264 | 97.1% | — |
| **SPL (Ours)** | **$89.47** | **38 ± 142** | **96.9%** | **94.5%** |

### Layer Distribution

| Layer | Requests | Percentage | Cost Contribution |
|-------|----------|------------|-------------------|
| Layer 0 (Reactive) | 4,823 | 4.8% | $0.00 (0.0%) |
| Layer 1 (Tactical) | 89,672 | 89.7% | $8.97 (10.0%) |
| Layer 2 (Deliberative) | 5,505 | 5.5% | $80.50 (90.0%) |

*Despite handling only 5.5% of requests, Layer 2 accounts for 90% of costs—validating the economic case for hierarchical suppression.*

### Multi-Agent Swarm Learning

| Agent | Tasks | Isolated ρ | Swarm ρ | Improvement |
|-------|-------|-----------|---------|-------------|
| Agent A | 1–20,000 | 87.2% | 87.2% | — |
| Agent B | 20,001–40,000 | 88.1% | 93.4% | +6.0% |
| Agent C | 40,001–60,000 | 87.9% | 95.7% | +8.9% |
| Agent D | 60,001–80,000 | 88.3% | 96.8% | +9.6% |
| Agent E | 80,001–100,000 | 88.0% | 97.2% | +10.4% |
| **Average** | — | 87.9% | **94.1%** | **+7.0%** |

**Result:** 42% reduction in Layer 2 escalations compared to isolated agents.

### Ablation Study

| Configuration | Cost (USD) | Accuracy | Δ Accuracy |
|---------------|-----------|----------|------------|
| Full SPL | $89.47 | 96.9% | — |
| No Layer 0 | $89.47 | 96.9% | +0.0% |
| No Layer 1 | $1,192.84 | 98.1% | +1.2% |
| θ = 0.95 (stricter) | $142.31 | 97.6% | +0.7% |
| θ = 0.75 (looser) | $67.23 | 94.2% | -2.7% |
| No Shared State | $127.83 | 96.4% | -0.5% |

**Key findings:**
- Disabling Layer 1 increases cost **13.3×** while improving accuracy only 1.2%
- Default threshold θ = 0.87 optimizes the cost-accuracy tradeoff
- Shared State contributes **30% additional cost savings** through pattern reuse

---

## 🔐 Theoretical Guarantees

### Theorem 1: Accuracy Preservation

Let ε be the maximum error rate of patterns. Then SPL's overall accuracy satisfies:

```
Acc_SPL ≥ (1 - ε) · ρ + Acc_L2 · (1 - ρ)
```

**Corollary:** If ε ≤ 0.05 and Acc_L2 ≥ 0.98, then Acc_SPL ≥ 0.95 for all ρ.

### Theorem 3: Graceful Degradation

If Layer 2 becomes unavailable, the system maintains accuracy:

```
Acc_degraded = (1 - ε) · Γ(t*)
```

on inputs where I₁(x) = true.

This formalizes the **headless swarm property**: accumulated competencies persist even without centralized reasoning resources.

---

## 📚 Repository Structure

```
SPL-FRAMEWORK/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── spl_arxiv_paper.pdf          # Full paper with proofs
│
├── spl/
│   ├── __init__.py              # Package initialization
│   ├── agent.py                 # SPL Agent (Definition 1)
│   ├── layer0_reactive.py       # Structural validation
│   ├── layer1_tactical.py       # Pattern matching + inhibition
│   ├── layer2_deliberative.py   # Foundation model + distillation
│   ├── shared_state.py          # Collective memory protocol
│   ├── pattern.py               # Pattern class (Definition 2)
│   ├── cost_tracker.py          # Cost monitoring
│   └── mcp_integration.py       # MCP client support
│
├── examples/
│   ├── email_categorization.py  # Email triage (paper Section 6.1)
│   ├── multi_agent_swarm.py     # Swarm learning (paper Section 6.5)
│   └── intelligence_compounding.py  # Γ(n) curves (paper Section 6.6)
│
├── tests/
│   ├── test_layer0.py           # Validation tests
│   ├── test_layer1.py           # Pattern matching + inhibition tests
│   ├── test_layer2.py           # Distillation tests
│   ├── test_shared_state.py     # Collective memory tests
│   └── test_accuracy_bounds.py  # Theorem 1 verification
│
├── comparison/
│   └── baselines/               # FrugalGPT, RouteLLM comparisons
│
└── docs/
    ├── ARCHITECTURE.md          # Formal framework details
    ├── SHARED_STATE_PROTOCOL.md # Synchronization semantics
    ├── INTELLIGENCE_COMPOUNDING.md  # Theorem 2 proof
    └── BENCHMARKS.md            # Full experimental results
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=spl/

# Verify accuracy bounds (Theorem 1)
pytest tests/test_accuracy_bounds.py -v
```

---

## 🤖 Supported Foundation Models

SPL is **foundation model agnostic** via MCP:

| Provider | Models |
|----------|--------|
| **Anthropic** | Claude Opus 4.5, Sonnet 4.5, Haiku 4.5 |
| **OpenAI** | GPT-4o, GPT-4 Turbo |
| **Open Source** | Llama 3, Mistral, Mixtral |
| **Custom** | Fine-tuned, proprietary, on-premise |

---

## 📖 Citation

```bibtex
@article{cuce2026spl,
  title={Subsumption Pattern Learning: A Formal Framework for 
         Self-Distilling Swarm Intelligence Through Shared 
         Collective Memory},
  author={Cuce, Pamela},
  journal={arXiv preprint arXiv:2501.XXXXX},
  year={2026},
  institution={Tufts University}
}
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Good First Issues
- Implement additional pattern types (semantic embeddings)
- Add support for new foundation model providers
- Benchmark on additional datasets
- Improve documentation

---

## 📧 Contact

**Author:** Pamela Cuce — pamela.cuce@tufts.edu

**Resources:**
- 📄 [arXiv Paper](https://arxiv.org/abs/2501.XXXXX)
- 📚 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/daseinpbc/SPL-FRAMEWORK/issues)
- 💬 [Discussions](https://github.com/daseinpbc/SPL-FRAMEWORK/discussions)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

SPL builds on foundational research from:

- **Rodney A. Brooks** — Subsumption architecture (MIT, 1986)
- **Ronald C. Arkin** — Behavior-based robotics
- **Albert Bandura** — Social learning theory
- **James Kennedy & Russell Eberhart** — Swarm intelligence
- **Daniel Wegner** — Transactive memory systems

---

## 🚀 Roadmap

- [ ] **v4.0**: Automated pattern distillation with learned extractors
- [ ] **v4.1**: Adaptive threshold learning (θ, α optimization)
- [ ] **v4.2**: Cross-domain pattern transfer
- [ ] **v4.3**: Large-scale deployment (100+ agents)
- [ ] **v5.0**: Continuous learning from production traffic

---

**SPL provides a principled path toward AI systems that grow more intelligent with every transaction while maintaining robustness through decentralized resilience.**

*Made with ❤️ — Bringing 40+ years of robotics intelligence to modern foundation models.*
