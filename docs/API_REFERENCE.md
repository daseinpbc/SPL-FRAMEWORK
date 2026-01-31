# API Reference

Complete API documentation for the SPL Framework v4.0, aligned with the formal definitions in the paper (Cuce, 2026).

---

## SPLAgent (Definition 1)

The main orchestrator implementing the formal agent tuple **A = (P_local, S, theta, alpha, L)**.

### Initialization

```python
from spl import SPLAgent

agent = SPLAgent(
    theta=0.87,          # Confidence threshold (theta) for Layer 1 suppression
    alpha=0.6,           # Complexity threshold (alpha)
    eta=0.1,             # Learning rate (eta) for confidence reinforcement
    delta=0.05,          # Decay rate (delta) for confidence decay
    shared_state=None,   # SharedState reference (S), optional
    agent_id=None        # Agent identifier for provenance tracking
)
```

### Parameters

| Parameter | Symbol | Type | Default | Description |
|-----------|--------|------|---------|-------------|
| `theta` | theta | float | 0.87 | Confidence threshold for Layer 1 suppression (Definition 5) |
| `alpha` | alpha | float | 0.6 | Complexity threshold (Definition 7) |
| `eta` | eta | float | 0.1 | Learning rate for confidence reinforcement (Definition 11) |
| `delta` | delta | float | 0.05 | Decay rate for confidence decay (Definition 12) |
| `shared_state` | S | SharedState | None | Reference to shared collective memory (Definition 10) |
| `agent_id` | -- | str | None | Agent identifier for pattern provenance (A in Shared State) |

### Methods

#### `process(request: dict) -> dict`

Process a request through the three-layer hierarchy (Layer 0 -> Layer 1 -> Layer 2).

**Parameters:**
- `request` (dict): Dictionary containing:
  - `user_id` (str): User identifier
  - `content` (str): Content to process

**Returns:**
- `result` (str): Processing result (response y)
- `layer` (int): Which layer handled the request (0, 1, or 2)
- `cost` (float): Cost incurred (C_0, C_1, or C_2)
- `confidence` (float): Match confidence score (phi_p(x))
- `inhibition` (bool): Whether I_1(x) = true (Definition 5)
- `suppressed_layer2` (bool): Whether Layer 2 was suppressed

**Example:**
```python
result = agent.process({
    'user_id': 'user123',
    'content': 'URGENT: Server outage in production'
})
# {
#   'result': 'urgent',
#   'layer': 1,
#   'cost': 0.0001,
#   'confidence': 0.95,
#   'inhibition': True,
#   'suppressed_layer2': True
# }
```

#### `get_metrics() -> dict`

Return performance metrics including suppression rate (rho), cost breakdown, and pattern statistics.

---

## Layer 0: ReactiveLayer (Definition 2)

Deterministic structural validation.

```
L_0(x) = (ERROR, e) if not valid(x), else (PASS, x)
```

- **Cost**: C_0 = $0
- **Latency**: T_0 < 1ms

### Validation Types
- JSON schema validation
- RFC 5322 email format validation
- Permission/authorization checks
- Rate limiting enforcement

---

## Layer 1: TacticalLayer (Definition 3)

Pattern matching with inhibition signals using the effective pattern set:

```
P_eff = P_local ∪ {p in P_shared : C(p) >= theta_inherit}
```

- **Cost**: C_1 ~ $0.0001 per request
- **Latency**: T_1 < 10ms

### `add_pattern(name, matcher, responder, confidence)`

Add a pattern **p = (phi_p, psi_p, kappa_p)** to the local pattern set (Definition: Pattern).

**Parameters:**
| Parameter | Symbol | Type | Description |
|-----------|--------|------|-------------|
| `name` | -- | str | Unique identifier for the pattern |
| `matcher` | phi_p | str | Regex pattern or semantic matcher (X -> [0, 1]) |
| `responder` | psi_p | str | Response template (X -> Y) |
| `confidence` | C(p) | float | Initial confidence score (0.0 to 1.0) |

**Example:**
```python
agent.layer1.add_pattern(
    name='urgent',
    matcher=r'urgent|asap|emergency',  # phi_p
    responder='urgent',                 # psi_p
    confidence=0.95                     # C(p)
)
```

### `check_inhibition(request) -> bool`

Evaluate the inhibition signal I_1(x) (Definition 5):

```
I_1(x) = true if max_{p in P_eff} phi_p(x) >= theta AND complexity(x) <= alpha
```

---

## Layer 2: DeliberativeLayer (Definition 4)

Foundation model reasoning with pattern distillation.

```
L_2(x) = (SOLVED, L(x), distill(L, x))
```

- **Cost**: C_2 in [$0.01, $0.10] per request
- **Latency**: T_2 in [100, 500]ms

### `distill(input, output, trace) -> Pattern or None`

Pattern distillation (Definition 8, Algorithm 1): Extract a reusable pattern from a reasoning trace.

Returns a new pattern if `generalizable(trace)` is true, otherwise None.

---

## SharedState (Definition 10)

Collective memory enabling stigmergic coordination: **S = (P_shared, C, M, A)**.

### Initialization

```python
from spl import SharedState
import redis

redis_client = redis.Redis(host='localhost', port=6379)
shared_state = SharedState(
    client=redis_client,
    theta_inherit=0.75,    # Inheritance threshold
    sync_interval=100      # ms (bounded staleness guarantee)
)
```

### Parameters

| Parameter | Symbol | Type | Default | Description |
|-----------|--------|------|---------|-------------|
| `client` | -- | Redis | required | Redis client for backing store |
| `theta_inherit` | theta_inherit | float | 0.75 | Minimum confidence for pattern inheritance (Eq. 9) |
| `sync_interval` | Delta_t | int | 100 | Sync interval in ms (Definition 14) |

### Confidence Update Rules

**Reinforcement** (Definition 11): When pattern p successfully resolves input x:
```
C'(p) = C(p) + eta * (1 - C(p))
```

**Decay** (Definition 12): When pattern p produces incorrect response:
```
C'(p) = C(p) * (1 - delta)
```

### Pattern Publication (Definition 13)

When an agent distills a new pattern:
```
publish(p) : S <- S ∪ {(p, c_0, 1, A_i)}
```
where c_0 = 0.5 is the initial confidence.

---

## CostTracker

Real-time cost monitoring per layer.

### Methods

#### `get_layer_costs() -> dict`

Returns cost breakdown by layer.

#### `get_suppression_rate() -> float`

Returns current suppression rate rho (Definition 6).

---

## MCPClient

Foundation model agnostic integration via Model Context Protocol.

```python
from spl.mcp_integration import MCPClient
import anthropic

client = anthropic.Anthropic()
layer2_mcp = MCPClient(
    model="claude-sonnet-4-20250514",
    api_client=client,
)
```

Supported providers: Anthropic (Claude), OpenAI (GPT-4), open-source (Llama, Mistral), custom/on-premise models.

---

## Complexity Function (Definition 7)

```
complexity(x) = beta_1 * length(x) + beta_2 * entropy(x) + beta_3 * novelty(x, P)
```

where:
- `length(x)` = token count
- `entropy(x)` = information entropy of content
- `novelty(x, P) = 1 - max_p phi_p(x)` = distance from known patterns

**Default coefficients:** beta_1 = 0.3, beta_2 = 0.3, beta_3 = 0.4

---

*For the formal mathematical framework, see [ARCHITECTURE.md](ARCHITECTURE.md). For experimental results, see [BENCHMARKS.md](BENCHMARKS.md).*
