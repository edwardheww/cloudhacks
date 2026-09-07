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
from src.query_parser import ParsedQuery, parse_query

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
{where_clause}
ORDER BY embeddings.embedding <=> %s::extensions.vector
LIMIT %s;
"""


def build_search_query(parsed: ParsedQuery, pgvector: str, limit: int) -> tuple[str, list]:
    clauses = []
    parameters: list = [pgvector]

    if parsed.cuisine:
        clauses.append("LOWER(deals.cuisine) = LOWER(%s)")
        parameters.append(parsed.cuisine)

    if parsed.location:
        clauses.append("LOWER(deals.location) LIKE LOWER(%s)")
        parameters.append(f"%{parsed.location}%")

    if parsed.price:
        clauses.append("LOWER(deals.price) = LOWER(%s)")
        parameters.append(parsed.price)

    if parsed.date_range:
        clauses.append(
            "COALESCE(deals.start_date, '-infinity'::date) <= %s "
            "AND COALESCE(deals.expiry_date, 'infinity'::date) >= %s"
        )
        parameters.extend([parsed.date_range.end, parsed.date_range.start])

    where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    parameters.extend([pgvector, limit])
    return SEARCH_SQL.format(where_clause=where_clause), parameters


def search(query: str, limit: int = 5) -> tuple[ParsedQuery, list[dict]]:
    parsed = parse_query(query)
    vector = EmbeddingService().embed([query])[0]
    pgvector = vector_to_pgvector(vector)
    sql, parameters = build_search_query(parsed, pgvector, limit)

    with psycopg.connect(
        os.environ["DATABASE_URL"],
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)
            return parsed, list(cursor.fetchall())


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python scripts/search_deals.py "your food query"')

    parsed, results = search(" ".join(sys.argv[1:]))
    reasons = ", ".join(parsed.match_reasons()) or "no explicit filters"
    print(f"Detected filters: {reasons}")
    for result in results:
        score = float(result.pop("semantic_score"))
        print(f"{score:.1%} | {result['restaurant']} | {result['title']} | {result['location']}")


if __name__ == "__main__":
    main()
