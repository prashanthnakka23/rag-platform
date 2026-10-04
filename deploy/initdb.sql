CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id          BIGSERIAL PRIMARY KEY,
    document    TEXT        NOT NULL,
    chunk_index INT         NOT NULL,
    content     TEXT        NOT NULL,
    embedding   vector(384) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tune lists once the corpus size is known (week 3).
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
