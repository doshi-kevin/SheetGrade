# Roadmap coverage

This project has two goals: ship the best spreadsheet grader available, and cover the
pre-agent AI-engineering curriculum along the way. This file tracks the second goal,
so a scope change can be checked against it instead of assumed. See
[PROJECT_PLAN.md](PROJECT_PLAN.md) for what each part actually builds.

| Practice | Part(s) |
|---|---|
| Tokens, context window, sampling parameters | 7, 21 |
| Quantization, VRAM budgeting, self-hosted models, local inference | 7 |
| Open vs closed models, OpenAI-compatible APIs, routing | 7 |
| Embeddings, semantic search | 8, 17, 20 |
| Vector databases, indexing, similarity search, hybrid search | 17 |
| Chunking strategies | 16 |
| RAG: load, index, store, query, evaluate | 16, 17 |
| Reranking, query rewriting, metadata filtering, adaptive top-k | 17 |
| Classification, clustering, anomaly detection | 9, 20, 23 |
| Structured outputs, schema-constrained decoding | 9, 18, 21 |
| System / role / constraint prompting | 18, 21 |
| Few-shot via retrieved exemplars | 21, 22 |
| Context engineering: write, read, compress, isolate | 22 |
| Memory systems: working, episodic, semantic, procedural | 22 |
| Context failure modes, staleness, contradiction | 22 |
| Context security, prompt injection defence, trust boundaries | 21 |
| Evaluation, LLM-as-judge, faithfulness, citation accuracy | 4, 17, 21 |
| Function calling / tool use | 24 |

Agents, ReAct, multi-agent and MCP are deliberately out of scope. Part 24's API surface
is already a set of agent tools; wrapping it in MCP is the on-ramp to the next project,
not part of this one.
