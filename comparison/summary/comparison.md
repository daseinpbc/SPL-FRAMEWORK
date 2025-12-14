# Method comparison
This report compares SPL's layered approach with two baselines that call Gemini directly.

## Spl
- Accuracy: 88.00%
- Avg latency (ms): 6.7
- Avg cost/email (USD): 0.000001
- Cost vs LangChain: 0.01x
- Latency vs LangChain: 0.00x
- Token savings vs LangChain: 98.53%

## Langchain
- Accuracy: 98.10%
- Avg latency (ms): 2235.2
- Avg cost/email (USD): 0.000096
- Cost vs LangChain: 1.00x
- Latency vs LangChain: 1.00x
- Token savings vs LangChain: 0.00%

## Autogen
- Accuracy: 20.00%
- Avg latency (ms): 15736.9
- Avg cost/email (USD): 0.000251
- Cost vs LangChain: 2.62x
- Latency vs LangChain: 7.04x
- Token savings vs LangChain: -143.91%
