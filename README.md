# rag-platform

A retrieval-augmented generation service built the way you'd run one in production, not the way you'd demo one.

Most RAG projects stop at "it returns an answer." This one treats retrieval as a serving system: it exposes
metrics, it has a cost ceiling, it tells you when quality drifts, and it deploys through the same pipeline
twice without surprises.

Built by [Prashanth Nakka](https://www.linkedin.com/in/prashanthnakka) — 5 years of data platform operations,
now applied to LLM infrastructure.

---

## Why this exists

I spent five years on call for data pipelines. The thing that broke was almost never the transformation
logic — it was everything around it: a dependency that fired early, a schema that drifted, a job that got
slower until it missed its window.

LLM systems fail the same way, and most RAG write-ups ignore it entirely. A retrieval service returns 200
whether it found the right chunk or garbage. That's the gap this project is about.

## What it does

```
  documents ──▶ chunk ──▶ embed ──▶ pgvector
                                       │
  query ─────▶ embed ──▶ similarity search ──▶ top-k ──▶ LLM ──▶ answer
                 │              │                 │
                 └──────────────┴─────────────────┴──▶ metrics ──▶ Prometheus ──▶ Grafana
```

A FastAPI service with two endpoints:

- `POST /ingest` — chunk, embed and store a document
- `POST /query` — embed the question, retrieve top-k, generate an answer, return it with its sources

Everything in between is instrumented.

## Stack, and why

| Choice | Why this one |
| --- | --- |
| **Python + FastAPI** | Async by default, and the metrics middleware is three lines |
| **pgvector on Postgres** | One container instead of a separate vector database. Postgres is already in every stack I'd deploy into; a dedicated vector store is a second thing to operate for no gain at this size |
| **sentence-transformers** (local embeddings) | No per-call cost, no rate limits, reproducible. Swappable for a hosted model behind one interface |
| **Docker Compose** → **Kubernetes** | Compose for the inner loop, k8s because that's where it would actually run |
| **Prometheus + Grafana** | What I already use. This is the part of the project I actually care about |
| **Terraform** | Environment creation as code, same as every platform I've built |

## The metrics (the actual point)

Standard RAG demos measure nothing. This exposes:

| Metric | Why it matters |
| --- | --- |
| `rag_query_duration_seconds` (by stage: embed / search / generate) | Tells you *which* stage is slow, not just that the request was |
| `rag_retrieval_score` (histogram of top-1 similarity) | The drift signal. If this distribution shifts, retrieval quality moved before any user complained |
| `rag_retrieved_chunks_used` | Are you paying to stuff context the model ignores? |
| `rag_tokens_total` (prompt / completion) | Cost per query, which nobody tracks until the bill arrives |
| `rag_empty_retrieval_total` | Queries where nothing crossed the similarity threshold — the silent failure mode |

The Grafana dashboard ships in `deploy/grafana/`.

## Plan

| Week | Dates | Goal |
| --- | --- | --- |
| 1 | Oct 4–11 | Scope, repo, ingestion: chunking, embeddings, pgvector schema |
| 2 | Oct 12–18 | Retrieval and the API: `/query`, top-k, prompt assembly, Docker Compose running end to end |
| 3 | Oct 19–25 | Kubernetes manifests, Prometheus instrumentation, Grafana dashboard, Terraform for the infra |
| 4 | Oct 26–Nov 1 | Load test, cost write-up, documentation, teardown notes |

## Running it

```bash
cp .env.example .env          # set your model + LLM provider key
docker compose up -d          # postgres/pgvector + the service
curl -X POST localhost:8000/ingest -F "file=@docs/sample.md"
curl -X POST localhost:8000/query -H 'Content-Type: application/json' \
     -d '{"question": "what does the retrieval score metric tell me?"}'
```

Metrics at `localhost:8000/metrics`, Grafana at `localhost:3000`.

## Open questions

Things I expect to get wrong and want to find out:

- What chunk size actually wins here, and does the answer change by document type?
- At what corpus size does pgvector stop being the obvious choice?
- Does top-1 similarity actually correlate with answer quality, or am I measuring something that feels
  meaningful and isn't?
- What's the real cost per query once you count embeddings, storage and generation together?

Answers go in `docs/` as I find them.

## Status

Week 1. Scoping done, ingestion in progress.
