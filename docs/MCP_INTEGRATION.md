# MCP Integration Guide

This document covers protocol-based orchestration using the Model Context Protocol (MCP) in SPL.

## Overview

Each SPL layer is an independent MCP Server, enabling:

- **Foundation Model Agnostic:** Build once, deploy across Claude, GPT-4o, Llama, or custom models
- **Zero Vendor Lock-in:** Swap foundation models without touching Layers 0-1
- **Language Agnostic:** Build layers in Python, Node.js, Go, Rust—MCP handles protocol
- **Enterprise Safe:** Authentication, rate limiting, error handling at protocol level
- **Multi-Agent Networks:** Share patterns, validation rules, behaviors via MCP discovery

## Basic Usage

```python
import anthropic
from spl import SPLAgent
from spl.mcp_integration import MCPClient

client = anthropic.Anthropic()

# Create Layer 2 MCP client for any foundation model
layer2_mcp = MCPClient(
    model="claude-3-5-sonnet-20241022",
    api_client=client,
)

agent = SPLAgent()
agent.layer2 = layer2_mcp

result = agent.process({
    'user_id': 'user123',
    'content': 'Complex reasoning task.'
})
```

---

*For more details, see the main [README.md](../README.md).*
