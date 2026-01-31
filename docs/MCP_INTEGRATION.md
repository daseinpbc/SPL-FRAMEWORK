# MCP Integration Guide

Protocol-based orchestration using the Model Context Protocol (MCP) in SPL.

> SPL is **foundation model agnostic** -- Layer 2 can use any foundation model via MCP, ensuring zero vendor lock-in.

---

## Overview

Each SPL layer is an independent MCP Server, enabling:

- **Foundation Model Agnostic:** Build once, deploy across Claude, GPT-4, Llama, or custom models
- **Zero Vendor Lock-in:** Swap foundation models without touching Layers 0-1
- **Language Agnostic:** Build layers in Python, Node.js, Go, Rust -- MCP handles protocol
- **Enterprise Safe:** Authentication, rate limiting, error handling at protocol level
- **Multi-Agent Networks:** Share patterns, validation rules, behaviors via MCP discovery

---

## Basic Usage

```python
import anthropic
from spl import SPLAgent
from spl.mcp_integration import MCPClient

client = anthropic.Anthropic()

# Create Layer 2 MCP client for any foundation model
layer2_mcp = MCPClient(
    model="claude-sonnet-4-20250514",
    api_client=client,
)

agent = SPLAgent(
    theta=0.87,    # Confidence threshold
    alpha=0.6,     # Complexity threshold
)
agent.layer2 = layer2_mcp

result = agent.process({
    'user_id': 'user123',
    'content': 'Complex reasoning task.'
})
```

---

## Supported Foundation Models

| Provider | Models | Notes |
|----------|--------|-------|
| **Anthropic** | Claude Opus 4.5, Claude Sonnet 4, Claude Haiku | Recommended for Layer 2 |
| **OpenAI** | GPT-4o, GPT-4 Turbo | Paper benchmarks used gpt-4-turbo |
| **Open Source** | Llama 3, Mistral, Mixtral | Via compatible API endpoints |
| **Custom** | Fine-tuned, proprietary, on-premise | Any MCP-compatible endpoint |

---

## Multi-Agent Configuration with MCP

```python
from spl import SPLAgent, SharedState
from spl.mcp_integration import MCPClient
import anthropic
import redis

# Shared State for collective memory
redis_client = redis.Redis(host='localhost', port=6379)
shared_state = SharedState(
    client=redis_client,
    theta_inherit=0.75,
    sync_interval=100
)

client = anthropic.Anthropic()

# Create swarm with shared Layer 2 provider
agents = []
for i in range(5):
    agent = SPLAgent(
        shared_state=shared_state,
        agent_id=f'agent_{i}',
        theta=0.87,
        alpha=0.6,
    )
    agent.layer2 = MCPClient(
        model="claude-sonnet-4-20250514",
        api_client=client,
    )
    agents.append(agent)

# Patterns distilled by any agent become available to all
# via the Shared State (Definition 13: Pattern Publication)
```

---

## Architecture

```
┌──────────────────────────────────────────────┐
│                 SPL Agent                      │
├──────────────────────────────────────────────┤
│  Layer 0: Reactive    (local, deterministic)   │
│  Layer 1: Tactical    (local, pattern match)   │
│  Layer 2: Deliberative (MCP -> Foundation Model)│
└──────────────────┬───────────────────────────┘
                   │ MCP Protocol
                   ↓
┌──────────────────────────────────────────────┐
│           Foundation Model Provider            │
│  Claude / GPT-4 / Llama / Custom               │
└──────────────────────────────────────────────┘
```

Key benefit: Layers 0 and 1 operate independently of the foundation model choice. Only Layer 2 uses MCP, and switching providers requires changing only the MCPClient configuration.

---

*For API details, see [API_REFERENCE.md](API_REFERENCE.md). For the full framework, see [ARCHITECTURE.md](ARCHITECTURE.md).*
