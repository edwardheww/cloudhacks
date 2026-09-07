"""Reusable AI search engine for the future FastAPI layer."""

from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

from src.embedding_service import EmbeddingService, vector_to_pgvector
from src.query_parser import ParsedQuery, parse_query

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

_embedding_service: EmbeddingService | None = None

DEAL_FIELDS = """
    id, restaurant, title, cuisine, location, discount, price,
    start_date, expiry_date, promo_code, source, source_url
"""

GET_DEAL_SQL = f"SELECT {DEAL_FIELDS} FROM deals WHERE id = %s;"

LIST_DEALS_SQL = f"""
SELECT {DEAL_FIELDS} FROM deals
WHERE COALESCE(expiry_date, 'infinity'::date) >= CURRENT_DATE
ORDER BY expiry_date ASC NULLS LAST, id
LIMIT %s;
"""

SEARCH_SQL = """
SELECT
    deals.id,
    deals.restaurant,
    deals.title,
    deals.cuisine,
    deals.location,
    deals.discount,
    deals.price,
    deals.start_date,
    deals.expiry_date,
    deals.promo_code,
    deals.source,
    deals.source_url,
    1 - (embeddings.embedding <=> %s::extensions.vector) AS semantic_score
FROM embeddings
JOIN deals ON deals.id = embeddings.deal_id
{where_clause}
ORDER BY embeddings.embedding <=> %s::extensions.vector
LIMIT %s;
"""


def get_embedding_service() -> EmbeddingService:
    """Return one shared model instance for the lifetime of the backend process."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def _build_search_query(parsed: ParsedQuery, pgvector: str, limit: int) -> tuple[str, list]:
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


def _json_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def search(query: str, limit: int = 5) -> list[dict]:
    """Return the best matching active/filter-compatible deals for a query.

    This function is the interface the FastAPI layer should call. It returns
    JSON-ready dictionaries, so the caller does not need to know about vectors,
    SQL, or query parsing.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return []
    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")

    parsed = parse_query(cleaned_query)
    vector = get_embedding_service().embed([cleaned_query])[0]
    sql, parameters = _build_search_query(parsed, vector_to_pgvector(vector), limit)

    with psycopg.connect(
        os.environ["DATABASE_URL"],
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)
            rows = cursor.fetchall()

    reasons = parsed.match_reasons()
    results = []
    for row in rows:
        result = {key: _json_value(value) for key, value in row.items()}
        result["semantic_score"] = round(float(result["semantic_score"]), 4)
        result["match_reasons"] = reasons
        results.append(result)
    return results


def list_deals(limit: int = 20) -> list[dict]:
    """Return currently-active deals with no query-dependent match info —
    used for browsing (e.g. an empty search) rather than a semantic query.

    This is the interface the FastAPI layer's `/deals` route should call.
    """
    with psycopg.connect(
        os.environ["DATABASE_URL"],
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(LIST_DEALS_SQL, (limit,))
            rows = cursor.fetchall()

    return [{key: _json_value(value) for key, value in row.items()} for row in rows]


def get_deal(deal_id: str) -> dict | None:
    """Return one deal by id, with no query-dependent match info attached.

    This is the interface the FastAPI layer's deal-detail route should call.
    """
    with psycopg.connect(
        os.environ["DATABASE_URL"],
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_DEAL_SQL, (deal_id,))
            row = cursor.fetchone()

    if row is None:
        return None
    return {key: _json_value(value) for key, value in row.items()}
