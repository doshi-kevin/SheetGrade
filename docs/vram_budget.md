# VRAM budget

Hardware: RTX 5060 Laptop GPU, 8GB VRAM.

| Model | Purpose | Quantization | Parameters | Measured GPU footprint |
|---|---|---|---|---|
| `llama3.2:3b` | generation / classification | Q4_K_M | 3.2B | 2.6GB (`ollama ps`) |
| `nomic-embed-text` | embedding | F16 | 137M | ~0.3GB (`ollama list`) |

Both resident at once: ~2.9GB of 8GB. Free at idle, measured via `nvidia-smi` on 2026-09-11: 4.8GB.

PROJECT_PLAN.md's Part 7 text predicted an 8GB card would force sequential loading (load one model, unload it, load the next) at "~0.6GB per billion parameters at Q4." That number was written before any model was chosen, and implicitly assumed something in the 7-8B range. The models actually installed are much smaller, so both stay loaded simultaneously with no sequential loading needed for Parts 7-9's scope.

Revisit this if a future part adds another resident model (e.g. Part 17's cross-encoder reranker): check its parameter count against the ~0.6GB/B-at-Q4 rule of thumb, and remember the KV-cache (the model's per-request scratch memory, which grows with how much text is sent per call) needs headroom on top of the weights themselves.
