# LangChain baseline

This baseline sends each email directly to a Groq chat model via LangChain without
state sharing or suppression. Every email invokes the LLM independently.

- Accuracy: 98.10%
- Average latency (ms): 2235.21
- Average cost per email (USD): 0.000096
Because there is no pattern learning across emails, token and cost scales linearly with the dataset size.