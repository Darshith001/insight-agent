# InsightAgent

Agentic multi-modal RAG platform with self-correcting reasoning, hybrid retrieval, and full LLMOps.

## Stack
LangGraph · Qdrant · BGE-M3 · BGE-reranker-v2 · Docling · ColPali · Claude 4.7/4.5 · vLLM · Unsloth (LoRA) · RAGAS · Langfuse · FastAPI · Next.js 14 · Redis · Postgres · Docker · k3s · Argo CD

## Quick start

```bash
# 1. infra
docker compose -f infra/docker-compose.yml up -d

# 2. python deps
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# 3. ingest a doc
python -m services.ingestion.pipeline ./samples/whitepaper.pdf

# 4. run API
uvicorn apps.api.app.main:app --reload --port 8000

# 5. run frontend
cd apps/web && pnpm i && pnpm dev
```

Open http://localhost:3000.

## Layout
```
apps/api          FastAPI gateway + SSE streaming
apps/web          Next.js 14 chat UI
services/agent    LangGraph state machine (plan→retrieve→synth→critique→retry)
services/ingestion Docling parser + BGE-M3 embedder + Qdrant upsert
services/router   Fine-tuned DistilBERT complexity classifier
evals             RAGAS golden set + CI eval gate
infra             docker-compose, k8s, Argo CD
scripts           Training, benchmarks, dataset gen
```

## KPI targets
| Metric | Target |
|---|---|
| Faithfulness (RAGAS) | > 0.88 |
| Context Recall@8 | > 0.85 |
| p95 latency | < 4.5 s |
| Cost / query | < $0.005 |

See `AI_Engineer_Project_Agentic_RAG.pdf` for full design rationale.
