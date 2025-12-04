# API Reference

Complete API documentation for the SPL Framework.

## SPLAgent

The main orchestrator for processing requests through the 3-layer architecture.

### Initialization

```python
from spl import SPLAgent

agent = SPLAgent()
```

### Methods

#### `process(request: dict) -> dict`

Process a request through all layers.

**Parameters:**
- `request`: Dictionary containing:
  - `user_id`: User identifier
  - `content`: Content to process

**Returns:**
- `result`: Processing result
- `layer`: Which layer handled the request (0, 1, or 2)
- `cost`: Cost incurred
- `confidence`: Confidence score
- `method`: Method used (pattern, cache, llm)

## Layer 0: Reactive

Validation and format checking.

## Layer 1: Tactical

Pattern matching and caching.

### `add_pattern(name, regex, category, confidence)`

Add a pattern to Layer 1.

## Layer 2: Deliberative

Foundation model integration.

---

*For more details, see the main [README.md](../README.md).*
