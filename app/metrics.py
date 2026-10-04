"""The metrics this project exists to expose.

A RAG service that returns 200 on a bad retrieval is the default. These are the
signals that make that failure visible.
"""

from prometheus_client import Counter, Histogram

QUERY_DURATION = Histogram(
    "rag_query_duration_seconds",
    "Time spent per query stage",
    labelnames=("stage",),  # embed | search | generate
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

RETRIEVAL_SCORE = Histogram(
    "rag_retrieval_score",
    "Cosine similarity of the top-ranked chunk. A shift in this distribution is "
    "the earliest signal that retrieval quality has drifted.",
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)

CHUNKS_USED = Histogram(
    "rag_retrieved_chunks_used",
    "Chunks that cleared the similarity threshold and entered the prompt. "
    "Consistently below top_k means you are paying to retrieve context you discard.",
    buckets=(0, 1, 2, 3, 4, 5, 8, 10),
)

TOKENS = Counter(
    "rag_tokens_total",
    "Tokens billed, split by direction — cost per query, before the invoice.",
    labelnames=("kind",),  # prompt | completion
)

EMPTY_RETRIEVAL = Counter(
    "rag_empty_retrieval_total",
    "Queries where nothing crossed the similarity threshold. The silent failure: "
    "the endpoint still returns 200 and the model still answers.",
)

INGESTED_CHUNKS = Counter(
    "rag_ingested_chunks_total",
    "Chunks written to the store.",
)
