# AutoGen baseline

Two lightweight agents collaborate: one proposes a label and another reviews it. There is no shared world state or suppression logic; each email triggers a short conversation.

- Accuracy: 20.00%
- Average latency (ms): 15736.91
- Average cost per email (USD): 0.000251
Because both agents can call the model, token usage is typically higher than the SPL layered approach.