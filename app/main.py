"""rag-platform — API surface.

Week 1 skeleton: the endpoints and the metrics exist and are wired up.
Ingestion and retrieval land in weeks 1 and 2 respectively.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.metrics import EMPTY_RETRIEVAL, QUERY_DURATION

app = FastAPI(title="rag-platform", version="0.1.0")


class Query(BaseModel):
    question: str
    top_k: int | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict[str, object]:
    """Chunk, embed and store a document. Week 1."""
    raise NotImplementedError("week 1: chunking + embeddings + pgvector insert")


@app.post("/query")
async def query(q: Query) -> dict[str, object]:
    """Embed the question, retrieve top-k, generate an answer. Week 2.

    Every stage times itself separately — knowing the request took 900ms is
    useless; knowing 700ms of it was generation is actionable.
    """
    with QUERY_DURATION.labels(stage="embed").time():
        pass
    with QUERY_DURATION.labels(stage="search").time():
        pass
    with QUERY_DURATION.labels(stage="generate").time():
        pass

    EMPTY_RETRIEVAL.inc(0)
    raise NotImplementedError("week 2: retrieval + prompt assembly + generation")
