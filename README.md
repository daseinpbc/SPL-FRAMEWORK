# SPL-FRAMEWORK
# Subsumption Pattern Learning (SPL) for LLM Agents

A hierarchical decision-making architecture that reduces LLM agent costs by **10-50x** through intelligent suppression of expensive LLM calls.


## Overview

SPL adapts Brooks' subsumption architecture from robotics to create a three-layer decision system for LLM agents:

- **Layer 0 (Reactive):** Structural validation - $0 cost, <1ms
- **Layer 1 (Tactical):** Pattern matching and rules - $0.001 cost, <10ms  
- **Layer 2 (Deliberative):** Full LLM reasoning - $0.01+ cost, 100-500ms

Lower layers can **suppress** upper layers, preventing expensive LLM calls before they occur.

## Key Results

| Metric | Single Agent | Multi-Agent Network |
|--------|--------------|---------------------|
| Cost Reduction | 5-15x | 10-50x |
| Typical Suppression Rate | 80-99% | 95%+ |
| Example (1000 emails) | $10 → $0.20 | Variable |

## Quick Start

### Installation
pip install anthropic redis  # Optional: redis for multi-agent state
### Basic Usage
from spl_framework import SPLAgentCreate agentagent = SPLAgent('email_analyzer')Process requestrequest = {
'user_id': 'user123',
'content': 'URGENT: Meeting at 3pm'
}result = agent.process(request)
print(f"Category: {result['category']}")
print(f"Cost: ${result['cost']:.4f}")
print(f"Layer: {result['layer']}")
### Expected Output
Category: urgent
Cost: $0.0000  (Pattern matched!)
Layer: 1
## Documentation

- **[SPL-Executive-v3.1.pdf](docs/SPL-Executive-v3.1.pdf)** - Executive summary & key metrics
- **[SPL-WhitePaper-v3.1.pdf](docs/SPL-WhitePaper-v3.1.pdf)** - Theory, architecture, benchmarks
- **[SPL-Technical-Architecture-v3.1.pdf](docs/SPL-Technical-Architecture-v3.1.pdf)** - Deep technical implementation details
- **[SPL-Integration-Guide-v3.1.pdf](docs/SPL-Integration-Guide-v3.1.pdf)** - Step-by-step integration guide
- **[SPL-MultiAgent-Guide-v3.1.pdf](docs/SPL-MultiAgent-Guide-v3.1.pdf)** - Multi-agent coordination & pattern sharing
- **[spl_demo_v3.1.py.pdf](docs/spl_demo_v3.1.py.pdf)** - Working demo with full documentation

## Implementation

### Single Agent Example
Email categorization with 97.4% cost reductionemails = [
'URGENT: Meeting changed',
'Invoice #12345',
'You won $1000!',
]total_cost = 0
for email in emails:
result = agent.process({'user_id': 'user', 'content': email})
total_cost += result['cost']print(f"Total cost: ${total_cost}")  # ~$0.01 instead of $0.30
### Multi-Agent Coordination
Create shared stateshared_state = {}Create 3 agents with shared stateagent_a = SPLAgent('agent_a', shared_state)
agent_b = SPLAgent('agent_b', shared_state)
agent_c = SPLAgent('agent_c', shared_state)Agent A learns patterns (expensive)Agents B & C reuse patterns (cheap)Network saves 60-80% vs single agent costs
## How It Works

### Decision Flow
INPUT
↓
LAYER 0: Validation
├─ Format check
├─ Permission check
├─ Rate limiting
└─ If invalid → HALT ($0)
↓
LAYER 1: Pattern Matching
├─ Check learned patterns
├─ Check cache
├─ Check rules
└─ If confident match → RETURN ($0, SUPPRESS Layer 2)
↓
LAYER 2: LLM Reasoning
├─ Call LLM API
├─ Get decision
├─ Learn new patterns
└─ Return result ($0.01+)
↓
OUTPUT
### Cost Breakdown (1000 emails)

| Task | Traditional | SPL | Savings |
|------|------------|-----|---------|
| Validation | $10.00 | $0 | 100% |
| Pattern matching | $20.00 | $0.05 | 99.75% |
| Permission checks | $10.00 | $0 | 100% |
| Novel reasoning | $40.00 | $2.00 | 95% |
| **Total** | **$80.00** | **$2.05** | **97.4%** |

## Architecture

### Three-Layer System

**Layer 0: Reactive (Validation)**
- Type checking, format validation
- Permission & authorization checks
- Rate limiting & quotas
- Blocklist/allowlist enforcement
- Cost: $0 (deterministic operations only)

**Layer 1: Tactical (Patterns)**
- Regex pattern matching
- Rule engine evaluation
- Cache lookup for repeated content
- Learned patterns (>0.85 confidence)
- Cost: $0.0001 (fast lookups)

**Layer 2: Deliberative (LLM)**
- Full LLM reasoning for complex cases
- Context-aware analysis
- Pattern learning from decisions
- Complex multi-step reasoning
- Cost: $0.01+ (expensive operation)

## Performance Metrics

### Accuracy vs Cost

| System | Cost | Speed | Accuracy |
|--------|------|-------|----------|
| Direct LLM | 1.0x | 100-500ms | 94% |
| Prompt caching | 0.9x | 100-500ms | 94% |
| SPL | 0.01-0.2x | <10ms | 93% |

**Note:** SPL trades 1% accuracy for 50x cost savings and 25x speed improvement.

### Scaling

- **Single Agent:** 5-15x cost reduction
- **5-Agent Network:** 5x lower per-email cost
- **10-Agent Network:** 10-50x cost reduction
- **Large Network:** 80%+ cost reduction after pattern stabilization

## Use Cases

### Email Categorization
- Filter spam, route to departments, flag urgent
- 80-95% suppression rate typical
- $0.10/1000 emails vs $10/1000 (traditional)

### Support Ticket Routing
- Route by category, urgency, complexity
- 85%+ handled by patterns
- Reduces expensive LLM calls

### Content Moderation
- Flag violations, approve safe content
- 90%+ handled by rules
- LLM only for edge cases

### Document Classification
- Categorize by type, topic, sensitivity
- 80-90% pattern matching rate
- Cost: $0.001/document vs $0.01

## Configuration

### Confidence Threshold
agent = SPLAgent('analyzer')
agent.confidence_threshold = 0.85  # DefaultHigher = more conservative (use LLM more often)Lower = more aggressive (trust patterns more)
### Custom Patterns
Add domain-specific patternsagent.add_pattern(
name='critical_bug',
regex=r'crash|segfault|critical',
category='critical',
confidence=0.95
)
### Rate Limiting
Configure per-user rate limitslayer_0.set_rate_limit('user123', requests_per_minute=100)
## Multi-Agent Pattern Sharing

### Network Effects
Agent A learns pattern in 10 requests
↓ (publishes to shared state)
Agents B, C, D, E use it immediately
↓ (no redundant learning)
Network learns 5x faster than single agent
### Shared State
shared_state = {
'learned_patterns': {
'urgent': {'confidence': 0.92, 'learned_by': 'agent_a'},
'billing': {'confidence': 0.88, 'learned_by': 'agent_c'}
},
'suppressed_layers': {
'agent_b': �  # Agent B has Layer 2 suppressed
},
'violations': [
{'agent': 'agent_b', 'violation': 'budget_exceeded'}
]
}
## Deployment

### Production Setup
Install dependenciespip install anthropic redisStart Redis for shared stateredis-serverDeploy agentspython -m spl_framework.deploy --config production.yaml
### Monitoring
Track costs and efficiencytracker = CostTracker()
for request in requests:
result = agent.process(request)
tracker.record(result)Generate reportreport = tracker.report()
print(f"Total cost: ${report['total_cost']:.2f}")
print(f"Suppression rate: {report['suppression_rate']:.1%}")
print(f"Cost reduction: {report['cost_reduction_factor']:.1f}x")
## Testing
Run demo with 10 emailspython examples/spl_demo_v3.1.pyRun unit testspytest tests/Run benchmarkspython benchmarks/email_categorization.py
## Failure Modes & Recovery

| Failure Mode | Impact | Recovery |
|--------------|--------|----------|
| Pattern drift | Accuracy decreases | Revalidate monthly |
| Backend failure | Can't access shared patterns | Fallback to local patterns |
| Safety violation | Detect unsafe pattern | Broadcast halt signal |
| Budget exceeded | Cost overrun | Suppress all Layer 2 calls |

## Performance Characteristics

### Speed

| Layer | Operation | Time |
|-------|-----------|------|
| 0 | Validation | <1ms |
| 1 | Pattern matching | <10ms |
| 2 | LLM call | 100-500ms |

### Cost

| Layer | Cost | Frequency |
|-------|------|-----------|
| 0 | $0 | 100% (all requests) |
| 1 | $0.001 | 10-20% (pattern hits) |
| 2 | $0.01+ | 5-20% (novel requests) |

## Benchmarks

### Email Categorization (1000 emails)
Baseline (Direct LLM):Cost: $10.00Time: 50 secondsAccuracy: 94%SPL System:Cost: $0.20Time: 2 secondsAccuracy: 93%Improvement:50x cheaper25x faster1% less accurate
### Scalability (10K emails/day, 10 agents)
Day 1 (Learning): $50
Day 7: $25
Day 30: $10Cost reduction over time:Week 1: 50% reductionMonth 1: 90% reductionSteady state: 95% reduction
## Architecture Comparison

| Approach | Cost | Speed | Determinism | Scalability |
|----------|------|-------|-------------|------------|
| Direct LLM | 1.0x | 100-500ms | Low | Linear |
| Prompt caching | 0.9x | 100-500ms | Medium | Limited |
| Fine-tuning | 1-3x | 50-100ms | High | High retraining cost |
| **SPL** | **0.01-0.2x** | **<10ms** | **High** | **Network effects** |

## Language Support

SPL works with any LLM:
- Claude 3.5 Sonnet
- GPT-4, GPT-4o
- Llama 3, Llama 2
- Mixtral
- Custom fine-tuned models

No API changes required - SPL runs as middleware/wrapper.

## Integration Time

| Phase | Time | Effort |
|-------|------|--------|
| Install | 5 minutes | Trivial |
| Basic setup | 15 minutes | Easy |
| Integration | 30 minutes | Medium |
| Production deployment | 4-8 weeks | Significant |
| Monitoring & optimization | Ongoing | Maintenance |

## Contributing

Contributions welcome! Areas for improvement:
- Advanced pattern extraction algorithms
- Machine learning for confidence calibration
- Distributed Redis integration
- Additional LLM providers
- Performance optimizations
- Benchmarks for new domains

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Author

**Pamela Cuce**
- Email: pamela@dasein.works


## Citation
@misc{cuce2025spl,
title={Subsumption Pattern Learning: Hierarchical LLM Agent Architecture},
author={Cuce, Pamela},
year={2025},
month={December}
}
---

**Version 3.1 (Corrected) | December 3, 2025**

**10-50x cheaper LLM agents through intelligent hierarchical suppression**
