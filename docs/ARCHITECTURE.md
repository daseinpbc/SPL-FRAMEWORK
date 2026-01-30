# SPL Architecture: Formal Framework

This document provides the complete mathematical formalization of Subsumption Pattern Learning (SPL), as presented in the paper:

> *Subsumption Pattern Learning: A Formal Framework for Self-Distilling Swarm Intelligence Through Shared Collective Memory* (Cuce, 2026)

---

## Table of Contents

1. [Preliminaries and Notation](#1-preliminaries-and-notation)
2. [Three-Layer Architecture](#2-three-layer-architecture)
3. [Inhibition Signal Formalization](#3-inhibition-signal-formalization)
4. [Pattern Distillation Process](#4-pattern-distillation-process)
5. [Shared State Protocol](#5-shared-state-protocol)
6. [Theoretical Analysis](#6-theoretical-analysis)
7. [Implementation Mapping](#7-implementation-mapping)

---

## 1. Preliminaries and Notation

Let **X** denote the input space of requests and **Y** the output space of responses.

### Definition: Pattern

A pattern **p = (φ_p, ψ_p, κ_p)** consists of:

| Component | Type | Description |
|-----------|------|-------------|
| **φ_p** | X → [0, 1] | Matcher returning match confidence |
| **ψ_p** | X → Y | Responder producing outputs for matched inputs |
| **κ_p** | ℝ⁺ | Complexity bound indicating maximum input complexity |

Let **P = {p₁, ..., pₙ}** denote the current pattern library and **S** the shared state containing patterns, confidence scores, and metadata.

### Definition 1: SPL Agent

An SPL agent is a tuple **A = (P_local, S, θ, α, L)** where:

| Parameter | Type | Description |
|-----------|------|-------------|
| **P_local** | Set of patterns | Agent's local pattern set |
| **S** | Shared State | Reference to collective memory |
| **θ** | (0, 1) | Confidence threshold for Layer 1 suppression |
| **α** | ℝ⁺ | Complexity threshold |
| **L** | X → Y | Layer 2 foundation model |

---

## 2. Three-Layer Architecture

### Definition 2: Layer 0 (Reactive/Structural Validation)

Layer 0 implements deterministic validation:

```
L₀(x) = ⎧ (ERROR, e)  if ¬valid(x)
        ⎨
        ⎩ (PASS, x)   otherwise
```

where `valid : X → {true, false}` checks structural constraints.

| Property | Value |
|----------|-------|
| Cost | C₀ = $0 (deterministic computation) |
| Latency | T₀ < 1ms |

**Examples:**
- JSON schema validation
- RFC 5322 email format validation
- Permission/authorization checks
- Rate limiting enforcement

### Definition 3: Layer 1 (Tactical/Pattern Matching)

Layer 1 attempts pattern-based resolution using the effective pattern set:

```
P_e = P_local ∪ {p ∈ S : conf(p) ≥ θ_inherit}
```

The layer function:

```
L₁(x) = ⎧ (MATCH, ψ_p*(x))  if ∃p* : φ_p*(x) ≥ θ ∧ complexity(x) ≤ α
        ⎨
        ⎩ (ESCALATE, x)     otherwise
```

where **p* = arg max_{p∈P_e} φ_p(x)**.

| Property | Value |
|----------|-------|
| Cost | C₁ ≈ $0.0001 per request |
| Latency | T₁ < 10ms |

### Definition 4: Layer 2 (Deliberative/Foundation Model Reasoning)

Layer 2 invokes the foundation model for unresolved requests:

```
L₂(x) = (SOLVED, L(x), distill(L, x))
```

where `distill(L, x)` extracts a candidate pattern from the reasoning trace.

| Property | Value |
|----------|-------|
| Cost | C₂ ∈ [$0.01, $0.10] per request |
| Latency | T₂ ∈ [100, 500]ms |

---

## 3. Inhibition Signal Formalization

The core mechanism of SPL is the **inhibition signal**, adapted from Brooks' subsumption architecture to operate on confidence scores rather than discrete triggers.

### Definition 5: Inhibition Signal

The Layer 1 inhibition signal **I₁ : X → {true, false}** is defined:

```
I₁(x) = ⎧ true   if max_{p∈P_e} φ_p(x) ≥ θ ∧ complexity(x) ≤ α
        ⎨
        ⎩ false  otherwise
```

**When I₁(x) = true, Layer 2 execution is suppressed.**

### Definition 6: Suppression Rate

The suppression rate **ρ** measures Layer 1 efficiency:

```
ρ = |{x ∈ X_test : I₁(x) = true}| / |X_test|
```

### Definition 7: Complexity Function

The complexity function `complexity : X → ℝ⁺` estimates reasoning difficulty:

```
complexity(x) = β₁ · length(x) + β₂ · entropy(x) + β₃ · novelty(x, P)
```

where:
- `length(x)` = token count
- `entropy(x)` = information entropy of content
- `novelty(x, P) = 1 - max_p φ_p(x)` = distance from known patterns

**Default coefficients:** β₁ = 0.3, β₂ = 0.3, β₃ = 0.4

### Conflict Resolution

When multiple patterns activate for input x:

```
p_selected = arg max_{p∈P_e} [φ_p(x) · C(p)]
```

The inhibition signal fires only if the weighted score exceeds threshold:

```
I₁(x) = ⎧ true   if φ_p_selected(x) · C(p_selected) ≥ θ
        ⎨
        ⎩ false  otherwise
```

---

## 4. Pattern Distillation Process

When Layer 2 solves a novel problem, SPL extracts a reusable pattern.

### Definition 8: Pattern Distillation

Given input x, Layer 2 output y = L(x), and reasoning trace τ, the distillation function `distill : (L, x) → P ∪ {∅}` produces a candidate pattern:

```
distill(L, x) = ⎧ (φ_new, ψ_new, κ_new)  if generalizable(τ)
                ⎨
                ⎩ ∅                       otherwise
```

where:
- **φ_new** = matcher derived from input features (regex, semantic embedding, or classifier)
- **ψ_new** = responder template parameterized by solution structure
- **κ_new** = complexity of original input x

### Algorithm 1: Pattern Distillation

```
Input: x, output y, reasoning trace τ, generalization threshold γ
Output: Candidate pattern p or ∅

1:  f_x ← featurize(x)                    # Extract input features
2:  t_y ← templatize(y)                   # Extract solution template
3:  g ← coverage(f_x, P_e)                # Estimate generalization score
4:  if g ≥ γ then
5:      φ_new ← build_matcher(f_x)
6:      ψ_new ← build_responder(t_y)
7:      κ_new ← complexity(x)
8:      return (φ_new, ψ_new, κ_new)
9:  else
10:     return ∅
11: end if
```

### Definition 9: State Transition (Deliberative → Tactical)

The transition from Layer 2 (deliberative state s_D) to Layer 1 (tactical state s_T):

```
s_D --distill--> s_T  ⟺  ∃p = distill(L, x) ≠ ∅ : S' = S ∪ {p}
```

After this transition, future inputs matching p will be handled at Layer 1 rather than escalated to Layer 2.

---

## 5. Shared State Protocol

### Definition 10: Shared State

The Shared State is a tuple **S = (P_shared, C, M, A)** where:

| Component | Type | Description |
|-----------|------|-------------|
| **P_shared** | Set | Global pattern library |
| **C** | P_shared → [0, 1] | Pattern → confidence scores |
| **M** | P_shared → ℕ | Pattern → match counts (reinforcement) |
| **A** | P_shared → AgentID | Pattern provenance tracking |

### Pattern Inheritance Protocol

Each agent's effective pattern set combines local and shared patterns:

```
P_e^(i) = P_local^(i) ∪ {p ∈ P_shared : C(p) ≥ θ_inherit}
```

where θ_inherit is the inheritance threshold (typically 0.70–0.90).

### Definition 11: Confidence Reinforcement

When pattern p successfully resolves input x with user-verified correctness:

```
C'(p) = C(p) + η(1 - C(p))
```

where η ∈ (0, 1) is the learning rate.

### Definition 12: Confidence Decay

When pattern p produces an incorrect response:

```
C'(p) = C(p) · (1 - δ)
```

where δ ∈ (0, 1) is the decay rate.

**This implements stigmergic reinforcement:** successful patterns accumulate confidence like pheromone trails, while failed patterns decay.

### Definition 13: Pattern Publication

When agent A_i distills pattern p:

```
publish(p) : S ← S ∪ {(p, c₀, 1, A_i)}
```

where c₀ is the initial confidence (typically 0.5).

### Definition 14: Pattern Subscription

Agents poll S with period Δt:

```
P_e^(i)(t) = P_local^(i) ∪ {p ∈ S(t - Δt) : C(p) ≥ θ_inherit}
```

This provides **bounded staleness guarantees**: patterns discovered by any agent become available to all agents within Δt.

---

## 6. Theoretical Analysis

### Theorem 1: Accuracy Preservation

Let ε be the maximum error rate of patterns in P_e:

```
ε = max_{p∈P_e} P_{x~D}[ψ_p(x) ≠ y*(x) | φ_p(x) ≥ θ]
```

where y*(x) is the ground-truth response. Then SPL's overall accuracy satisfies:

```
Acc_SPL ≥ (1 - ε) · ρ + Acc_L2 · (1 - ρ)
```

where ρ is the suppression rate and Acc_L2 is Layer 2 accuracy.

**Proof:** Requests partition into suppressed (handled by Layer 1) and escalated (handled by Layer 2). For suppressed requests, accuracy is at least (1 - ε) by definition of ε. For escalated requests, accuracy is Acc_L2. The weighted sum follows by linearity. ∎

**Corollary 1:** If ε ≤ 0.05 and Acc_L2 ≥ 0.98, then Acc_SPL ≥ 0.95 for all ρ.

### Theorem 2: Intelligence Compounding

Under the following assumptions:
1. Inputs are drawn i.i.d. from distribution D
2. Each novel input has probability π > 0 of yielding a distillable pattern
3. Each distilled pattern covers a region of D with measure at least μ > 0
4. Pattern regions may overlap with existing patterns

The collective competency satisfies:

```
Γ(n) = 1 - e^(-πμn/k)
```

where n is the number of processed requests and k is a coverage constant.

**Corollary 2 (Logarithmic Learning):** To achieve competency Γ*, the swarm requires:

```
n* = (k/πμ) · ln(1/(1 - Γ*))
```

requests.

**Remark:** Multi-agent systems amplify this effect. If m agents share state and process independent request streams, the effective rate is m · π, reducing time to competency by factor m.

### Theorem 3: Graceful Degradation

If Layer 2 becomes unavailable at time t*, the system maintains accuracy:

```
Acc_degraded = (1 - ε) · Γ(t*)
```

on inputs where I₁(x) = true, and returns `unavailable` for remaining inputs.

This formalizes the **headless swarm property**: accumulated competencies persist even without centralized reasoning resources.

---

## 7. Implementation Mapping

### Code Structure

| Formal Concept | Implementation |
|----------------|----------------|
| SPL Agent (Def. 1) | `spl/agent.py::SPLAgent` |
| Pattern (p) | `spl/pattern.py::Pattern` |
| Matcher (φ_p) | `Pattern.match(x) → float` |
| Responder (ψ_p) | `Pattern.respond(x) → Y` |
| Layer 0 | `spl/layer0_reactive.py::ReactiveLayer` |
| Layer 1 | `spl/layer1_tactical.py::TacticalLayer` |
| Layer 2 | `spl/layer2_deliberative.py::DeliberativeLayer` |
| Inhibition (I₁) | `TacticalLayer.check_inhibition(x) → bool` |
| Shared State (S) | `spl/shared_state.py::SharedState` |
| Confidence (C) | `SharedState.get_confidence(p) → float` |
| Distillation | `DeliberativeLayer.distill(x, y, τ) → Pattern` |

### Default Hyperparameters

| Parameter | Symbol | Default | Paper Reference |
|-----------|--------|---------|-----------------|
| Confidence threshold | θ | 0.87 | Section 6.1.5 |
| Complexity threshold | α | 0.6 | Section 6.1.5 |
| Inheritance threshold | θ_inherit | 0.75 | Section 4.2 |
| Learning rate | η | 0.1 | Appendix A.3 |
| Decay rate | δ | 0.05 | Appendix A.3 |
| Initial confidence | c₀ | 0.5 | Section 4.5 |
| Sync interval | Δt | 100ms | Section 6.1.5 |
| Generalization threshold | γ | 0.7 | Algorithm 1 |

---

## References

- Brooks, R. A. (1986). A robust layered control system for a mobile robot. *IEEE Journal of Robotics and Automation*, 2(1):14–23.
- Arkin, R. C. (1989). Motor schema-based mobile robot navigation. *The International Journal of Robotics Research*, 8(4):92–112.
- Bandura, A. (1977). *Social Learning Theory*. Prentice Hall.
- Kennedy, J. and Eberhart, R. C. (2001). *Swarm Intelligence*. Morgan Kaufmann.
- Wegner, D. M. (1987). Transactive memory: A contemporary analysis of the group mind.
