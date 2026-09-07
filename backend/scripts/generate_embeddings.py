"""Generate BGE-M3 vectors for every deal in Supabase.

Run from the backend directory:
    python scripts/generate_embeddings.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.embedding_service import EmbeddingService, deal_to_embedding_text, vector_to_pgvector

load_dotenv(BACKEND_DIR / ".env")

UPSERT_EMBEDDING = """
INSERT INTO embeddings (deal_id, embedding)
VALUES (%s, %s::extensions.vector)
ON CONFLICT (deal_id) DO UPDATE SET
    embedding = EXCLUDED.embedding,
    created_at = NOW();
"""


def main() -> None:
    database_url = os.environ["DATABASE_URL"]

    with psycopg.connect(
        database_url,
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM deals ORDER BY id")
            deals = cursor.fetchall()

        if not deals:
            raise RuntimeError("No deals found. Run scripts/load_deals.py first.")

        texts = [deal_to_embedding_text(deal) for deal in deals]
        vectors = EmbeddingService().embed(texts)

        with connection.cursor() as cursor:
            for deal, vector in zip(deals, vectors, strict=True):
                cursor.execute(UPSERT_EMBEDDING, (deal["id"], vector_to_pgvector(vector)))

        connection.commit()

    print(f"Generated and stored {len(deals)} BGE-M3 embeddings.")


if __name__ == "__main__":
    main()
