# Benchmarks and Experimental Results

Complete experimental results from the SPL paper (Cuce, 2026), Section 6.

> **Paper:** *Subsumption Pattern Learning: A Formal Framework for Self-Distilling Swarm Intelligence Through Shared Collective Memory*

---

## 1. Experimental Setup

### 1.1 Dataset

We evaluate on a benchmark of **100,000 heterogeneous enterprise tasks** drawn from three production deployments:

| Domain | Tasks | Description |
|--------|-------|-------------|
| **Email Classification** | 40,000 | Categorization, priority assignment, routing |
| **Customer Inquiry Resolution** | 35,000 | FAQ matching, ticket classification, response generation |
| **Data Pipeline Orchestration** | 25,000 | Schema validation, transformation routing, error handling |

Tasks were collected over 6 months from consenting enterprise partners with PII removed. Ground-truth labels were assigned by domain experts with inter-annotator agreement **kappa = 0.89**.

### 1.2 Task Categorization

Tasks were independently categorized into latent complexity classes:

| Class | Layer | Percentage |
|-------|-------|------------|
| Deterministic | Layer 0 | 4.8% |
| Pattern-Matchable | Layer 1 | 89.7% |
| High-Entropy | Layer 2 | 5.5% |

### 1.3 Baselines

| System | Description |
|--------|-------------|
| **Monolithic LLM** | All requests processed by GPT-4-turbo |
| **FrugalGPT Cascade** | GPT-3.5 -> GPT-4 cascade with learned router (Chen et al., 2023) |
| **RouteLLM** | Preference-based routing between model tiers (Ong et al., 2024) |
| **SPL (Ours)** | Three-layer architecture with shared state |

### 1.4 Metrics

- **Cost**: Total API spend (USD)
- **Latency**: Mean time-to-first-token (TTFT) and end-to-end latency
- **Accuracy**: Agreement with expert labels
- **Suppression Rate (rho)**: Fraction resolved at Layer 0/1

### 1.5 Implementation Details

| Component | Configuration |
|-----------|---------------|
| **Layer 0** | JSON schema validation, content policy filters |
| **Layer 1** | Hybrid matcher: regex patterns + sentence-transformer embeddings (`all-MiniLM-L6-v2`) with cosine similarity threshold theta = 0.87 |
| **Layer 2** | GPT-4-turbo with structured output extraction |
| **Shared State** | Redis-backed store with 100ms sync interval |
| **Complexity threshold** | alpha = 0.6 (normalized scale) |

---

## 2. Single-Agent Results (Table 1)

| System | Cost (USD) | Latency (ms) | Accuracy | Suppression Rate |
|--------|-----------|--------------|----------|------------------|
| Monolithic LLM | $1,247.32 | 847 +/- 312 | 98.2% | 0.0% |
| FrugalGPT | $312.18 | 523 +/- 287 | 97.4% | -- |
| RouteLLM | $287.45 | 498 +/- 264 | 97.1% | -- |
| **SPL (Ours)** | **$89.47** | **38 +/- 142** | **96.9%** | **94.5%** |

**Key results:**
- **13.9x cost reduction** vs. monolithic LLM baseline
- **3.2x cost reduction** vs. FrugalGPT
- **22.3x latency improvement** (median) due to Layer 1's sub-10ms response times
- Accuracy within **1.3%** of baseline

---

## 3. Layer Distribution Analysis (Table 2)

| Layer | Requests | Percentage | Cost Contribution |
|-------|----------|------------|-------------------|
| Layer 0 (Reactive) | 4,823 | 4.8% | $0.00 (0.0%) |
| Layer 1 (Tactical) | 89,672 | 89.7% | $8.97 (10.0%) |
| Layer 2 (Deliberative) | 5,505 | 5.5% | $80.50 (90.0%) |
| **Total** | **100,000** | **100%** | **$89.47** |

Despite handling only 5.5% of requests, Layer 2 accounts for 90% of costs -- validating the economic motivation for suppression.

---

## 4. Ablation Study (Table 3)

| Configuration | Cost (USD) | Accuracy | Delta Accuracy |
|---------------|-----------|----------|----------------|
| Full SPL | $89.47 | 96.9% | -- |
| No Layer 0 | $89.47 | 96.9% | +0.0% |
| No Layer 1 | $1,192.84 | 98.1% | +1.2% |
| theta = 0.95 (stricter) | $142.31 | 97.6% | +0.7% |
| theta = 0.75 (looser) | $67.23 | 94.2% | -2.7% |
| No Shared State | $127.83 | 96.4% | -0.5% |

**Key findings:**
- Disabling Layer 1 increases cost **13.3x** while improving accuracy only 1.2%
- Default threshold theta = 0.87 optimizes the cost-accuracy tradeoff
- Shared State contributes **30% additional cost savings** through pattern reuse

### Extended Ablation: Varying Confidence Threshold theta (Table 6)

| theta | Cost (USD) | Accuracy | Suppression Rate |
|-------|-----------|----------|------------------|
| 0.70 | $52.31 | 91.2% | 97.8% |
| 0.75 | $67.23 | 94.2% | 96.4% |
| 0.80 | $78.45 | 95.8% | 95.3% |
| 0.85 | $86.12 | 96.7% | 94.8% |
| **0.87** | **$89.47** | **96.9%** | **94.5%** |
| 0.90 | $112.34 | 97.3% | 92.1% |
| 0.95 | $142.31 | 97.6% | 88.7% |

Lower thresholds reduce cost but sacrifice accuracy; higher thresholds preserve accuracy but increase cost. The optimal operating point (theta = 0.87) balances these objectives.

---

## 5. Multi-Agent Swarm Learning (Table 4)

5 concurrent agents processing disjoint task streams of 20,000 tasks each:

| Agent | Tasks | Isolated rho | Swarm rho | Improvement |
|-------|-------|-------------|-----------|-------------|
| Agent A | 1-20,000 | 87.2% | 87.2% | -- |
| Agent B | 20,001-40,000 | 88.1% | 93.4% | +6.0% |
| Agent C | 40,001-60,000 | 87.9% | 95.7% | +8.9% |
| Agent D | 60,001-80,000 | 88.3% | 96.8% | +9.6% |
| Agent E | 80,001-100,000 | 88.0% | 97.2% | +10.4% |
| **Average** | -- | **87.9%** | **94.1%** | **+7.0%** |

**Result:** 42% reduction in Layer 2 escalations compared to isolated agents, validating collective intelligence emergence.

Each successive agent benefits from patterns discovered by predecessors via the Shared State. While isolated agents plateau around 88% suppression, swarm agents achieve up to 97.2% suppression.

---

## 6. Intelligence Compounding Curves

The suppression rate rho increases logarithmically with cumulative requests processed, asymptotically approaching the theoretical maximum. The empirical curve closely matches the theoretical prediction from Theorem 2:

```
Gamma(n) = 1 - e^(-pi*mu*n/k)
```

The characteristic S-shape reflects pattern acquisition dynamics:
1. **Initial slow growth** as the pattern library builds
2. **Rapid improvement** as common cases are covered
3. **Eventual saturation** as the domain becomes well-characterized

---

## 7. Latency Analysis (Table 5)

| Layer | TTFT (ms) | End-to-End (ms) | p50 (ms) | p99 (ms) |
|-------|-----------|-----------------|----------|----------|
| Layer 0 | < 1 | < 1 | < 1 | 2 |
| Layer 1 | 3 | 8 | 6 | 24 |
| Layer 2 | 287 | 847 | 623 | 2,134 |
| **SPL Overall** | **14** | **38** | **7** | **892** |

Layer 1's median latency of 6ms enables real-time applications. The p99 latency of 892ms reflects the 5.5% of requests requiring Layer 2. SPL achieves a **22x improvement** in median response time vs. monolithic LLM.

---

## 8. Statistical Significance

All comparisons use **paired bootstrap tests** (n = 10,000 resamples):
- Cost and latency improvements vs. baselines are significant at **p < 0.001**
- The accuracy difference vs. monolithic LLM (-1.3%) is significant at **p < 0.01** but represents an acceptable tradeoff given 13.9x cost reduction

---

## 9. Scaling Dynamics

The table below illustrates how costs decrease over time as SPL learns patterns:

| Scenario | Daily Cost | Pattern Reuse |
|----------|-----------|---------------|
| Day 1 (Learning) | $6.50 | 40% |
| Day 7 (Optimization) | $2.50 | 75% |
| Day 30 (Steady State) | $0.50 | 95% |

**Assumptions:**
- ~1000 daily requests
- Foundation model cost: $0.01 per request
- Pattern matching cost: $0.001 per request

---

## Reproducibility Checklist (Paper Appendix A)

### Dataset
- Source: Enterprise partners (anonymized)
- Size: 100,000 tasks
- Splits: 80/10/10 train/validation/test
- Preprocessing: PII removal, JSON normalization
- Availability: Contact authors for access

### Implementation
- Language: Python 3.11
- Layer 1 embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Layer 2 model: `gpt-4-turbo-2024-04-09`
- Shared State: Redis 7.2 with RedisJSON

### Hyperparameters
| Parameter | Symbol | Value |
|-----------|--------|-------|
| Confidence threshold | theta | 0.87 |
| Complexity threshold | alpha | 0.6 |
| Inheritance threshold | theta_inherit | 0.75 |
| Learning rate | eta | 0.1 |
| Decay rate | delta | 0.05 |
| Sync interval | -- | 100ms |

---

*For the full formal framework, see [ARCHITECTURE.md](ARCHITECTURE.md). For the complete paper, see [spl_arxiv_paper.pdf](spl_arxiv_paper.pdf).*
