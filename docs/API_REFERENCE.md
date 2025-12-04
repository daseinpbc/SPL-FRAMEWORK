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

Add a pattern to Layer 1 for pattern matching.

**Parameters:**
- `name` (str): Unique identifier for the pattern
- `regex` (str): Regular expression to match against content
- `category` (str): Category to assign when pattern matches
- `confidence` (float): Confidence score for matches (0.0 to 1.0)

**Returns:**
- None

**Example:**
```python
agent.layer1.add_pattern(
    name='urgent',
    regex=r'urgent|asap|emergency',
    category='urgent',
    confidence=0.95
)
```

## Layer 2: Deliberative

Foundation model integration.

---

*For more details, see the main [README.md](../README.md).*
