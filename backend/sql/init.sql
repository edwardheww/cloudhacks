CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

CREATE TABLE deals (
    id TEXT PRIMARY KEY,
    raw_text TEXT NOT NULL,
    restaurant TEXT,
    title TEXT,
    cuisine TEXT,
    location TEXT,
    discount TEXT,
    price TEXT,
    start_date DATE,
    expiry_date DATE,
    promo_code TEXT,
    source TEXT,
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE embeddings (
    deal_id TEXT PRIMARY KEY REFERENCES deals(id) ON DELETE CASCADE,
    embedding extensions.vector(1024) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);