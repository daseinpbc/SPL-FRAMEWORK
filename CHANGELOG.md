# Changelog

All notable changes to the SPL Framework are documented here.

## [4.0.0] - 2026-01-30

### 🎓 Academic Publication

This release aligns the codebase with the formal framework presented in:

> **Subsumption Pattern Learning: A Formal Framework for Self-Distilling Swarm Intelligence Through Shared Collective Memory**  
> Pamela Cuce, Tufts University (January 2026)

### Added

#### Formal Framework (Paper Section 3)
- **Definition 1: SPL Agent** — Formal tuple definition `A = (P_local, S, θ, α, L)`
- **Definition 2: Pattern** — Pattern structure `p = (φ_p, ψ_p, κ_p)` with matcher, responder, complexity bound
- **Definition 3-4: Layer Definitions** — Formal specifications for Layer 0, 1, 2
- **Definition 5: Inhibition Signal** — Confidence-bounded suppression `I₁(x)`
- **Definition 6: Suppression Rate** — Metric `ρ` for Layer 1 efficiency
- **Definition 7: Complexity Function** — `complexity(x) = β₁·length(x) + β₂·entropy(x) + β₃·novelty(x,P)`

#### Shared State Protocol (Paper Section 4)
- **Definition 10: Shared State** — Tuple `S = (P_shared, C, M, A)` with patterns, confidence, match counts, provenance
- **Definition 11: Confidence Reinforcement** — `C'(p) = C(p) + η(1 - C(p))`
- **Definition 12: Confidence Decay** — `C'(p) = C(p) · (1 - δ)`
- **Definition 13-14: Synchronization Semantics** — Pattern publication and subscription protocols

#### Theoretical Analysis (Paper Section 5)
- **Theorem 1: Accuracy Preservation** — Provable accuracy bounds under suppression
- **Theorem 2: Intelligence Compounding** — Logarithmic competency growth `Γ(n) = 1 - e^(-πμn/k)`
- **Theorem 3: Graceful Degradation** — Headless swarm property

#### Experimental Results (Paper Section 6)
- Benchmark on **100,000 heterogeneous enterprise tasks**
- **13.9× cost reduction** vs. monolithic LLM baseline
- **3.2× cost reduction** vs. FrugalGPT cascade
- **94.5% suppression rate** with 96.9% accuracy
- Multi-agent swarm learning: **42% reduction** in Layer 2 escalations
- Ablation studies with statistical significance testing (p < 0.001)

### Changed

#### README.md
- Restructured to follow paper organization
- Added formal mathematical definitions
- Updated results tables with paper's experimental data
- Added Intelligence Compounding Theory section
- Updated citation to reference arxiv paper
- Added theoretical guarantees section

#### Configuration Parameters
- Default `θ = 0.87` (confidence threshold, optimized in ablation study)
- Default `α = 0.6` (complexity threshold)
- Default `η = 0.1` (learning rate)
- Default `δ = 0.05` (decay rate)
- Default `θ_inherit = 0.75` (inheritance threshold)
- Sync interval: 100ms (for distributed deployments)

### Implementation Details

#### Layer 1: Tactical/Pattern Matching
- Hybrid matcher: regex patterns + sentence-transformer embeddings
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Cosine similarity threshold: 0.87

#### Layer 2: Deliberative/Foundation Model
- Default: `gpt-4-turbo` (configurable via MCP)
- Structured output extraction for pattern distillation

#### Shared State
- Redis-backed store with RedisJSON
- Eventual consistency with bounded staleness guarantees

### Reproducibility

Added reproducibility checklist (Paper Appendix A):
- Dataset: 100K tasks from enterprise partners
- Splits: 80/10/10 train/validation/test
- Inter-annotator agreement: κ = 0.89
- All hyperparameters documented

---

## [3.1.0] - 2025-12-XX (Previous Release)

- Initial public release
- Three-layer architecture
- MCP integration
- Basic pattern matching

---

## Migration Guide: v3.1 → v4.0

### Parameter Changes

```python
# Old (v3.1)
agent = SPLAgent()

# New (v4.0) - explicit formal parameters
agent = SPLAgent(
    theta=0.87,      # Confidence threshold (θ)
    alpha=0.6,       # Complexity threshold (α)
    eta=0.1,         # Learning rate (η)  
    delta=0.05       # Decay rate (δ)
)
```

### Shared State Changes

```python
# Old (v3.1)
agent.share_patterns(other_agent)

# New (v4.0) - formal Shared State protocol
shared_state = SharedState(
    client=redis_client,
    theta_inherit=0.75
)
agents = [SPLAgent(shared_state=shared_state) for _ in range(5)]
```

### Result Object Changes

```python
# Old (v3.1)
result = agent.process(request)
print(result['suppressed'])

# New (v4.0) - formal inhibition signal
result = agent.process(request)
print(result['inhibition'])      # I₁(x) boolean
print(result['suppressed_layer2'])  # Whether Layer 2 was suppressed
print(result['confidence'])      # C(p) value
```
