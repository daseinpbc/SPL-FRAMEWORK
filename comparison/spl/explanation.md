# SPL run overview

SPL applies three layers of control: Layer 0 validates inputs, Layer 1 uses learned patterns to short-circuit repeated cases, and Layer 2 calls Gemini only when the earlier layers cannot decide.

Key observations for this run:
- Emails finalized by Layer 0: 0
- Emails finalized by Layer 1: 986 (patterns suppressed L2: 986)
- Emails requiring Layer 2 (Gemini): 14
- Suppression rate (Layer 2 avoided): 98.60%
- Accuracy: 88.00%
- Average latency (ms): 6.66
- Average cost per email (USD): 0.000001
- Final budget remaining (USD): None
- Total tokens used: 2312
- Safety violations recorded: 0

Lower layers reuse world state and learned patterns, so later emails can skip expensive model calls while keeping accuracy high.