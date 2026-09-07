"""Run a semantic-search query against embeddings stored in Supabase.

Example:
    python scripts/search_deals.py "cheap Thai food near Clementi"
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

from src.embedding_service import EmbeddingService, vector_to_pgvector

load_dotenv(BACKEND_DIR / ".env")

SEARCH_SQL = """
SELECT
    deals.id,
    deals.restaurant,
    deals.title,
    deals.cuisine,
    deals.location,
    deals.discount,
    deals.expiry_date,
    deals.source,
    deals.source_url,
    1 - (embeddings.embedding <=> %s::extensions.vector) AS semantic_score
FROM embeddings
JOIN deals ON deals.id = embeddings.deal_id
ORDER BY embeddings.embedding <=> %s::extensions.vector
LIMIT %s;
"""


def search(query: str, limit: int = 5) -> list[dict]:
    vector = EmbeddingService().embed([query])[0]
    pgvector = vector_to_pgvector(vector)

    with psycopg.connect(
        os.environ["DATABASE_URL"],
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(SEARCH_SQL, (pgvector, pgvector, limit))
            return list(cursor.fetchall())


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python scripts/search_deals.py "your food query"')

    results = search(" ".join(sys.argv[1:]))
    for result in results:
        score = float(result.pop("semantic_score"))
        print(f"{score:.1%} | {result['restaurant']} | {result['title']} | {result['location']}")


if __name__ == "__main__":
    main()
