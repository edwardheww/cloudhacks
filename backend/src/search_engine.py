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


def get_embedding_service() -> EmbeddingService:
    """Return one shared model instance for the lifetime of the backend process."""
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService()

    return _embedding_service


def _build_search_query(
    parsed: ParsedQuery,
    pgvector: str,
    limit: int,
) -> tuple[str, list]:
    """
    Build a semantic search query.

    Semantic similarity is the main ranking signal.
    Parsed cuisine/location/price/date information is used as
    a ranking boost rather than a hard filter.
    """

    boost_parts = []
    boost_parameters: list = []

    # Cuisine match = +0.10
    if parsed.cuisine:
        boost_parts.append(
            """
            CASE
                WHEN LOWER(deals.cuisine) = LOWER(%s)
                THEN 0.10
                ELSE 0
            END
            """
        )
        boost_parameters.append(parsed.cuisine)

    # Location match = +0.10
    if parsed.location:
        boost_parts.append(
            """
            CASE
                WHEN LOWER(deals.location) LIKE LOWER(%s)
                THEN 0.10
                ELSE 0
            END
            """
        )
        boost_parameters.append(f"%{parsed.location}%")

    # Price match = +0.05
    if parsed.price:
        boost_parts.append(
            """
            CASE
                WHEN LOWER(deals.price) = LOWER(%s)
                THEN 0.05
                ELSE 0
            END
            """
        )
        boost_parameters.append(parsed.price)

    # Date overlap = +0.10
    if parsed.date_range:
        boost_parts.append(
            """
            CASE
                WHEN
                    COALESCE(deals.start_date, '-infinity'::date) <= %s
                    AND
                    COALESCE(deals.expiry_date, 'infinity'::date) >= %s
                THEN 0.10
                ELSE 0
            END
            """
        )
        boost_parameters.extend(
            [
                parsed.date_range.end,
                parsed.date_range.start,
            ]
        )

    if boost_parts:
        boost_expression = " + ".join(boost_parts)
    else:
        boost_expression = "0"

    sql = f"""
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

        1 - (embeddings.embedding <=> %s::extensions.vector)
            AS semantic_score,

        (
            1 - (embeddings.embedding <=> %s::extensions.vector)
            + {boost_expression}
        ) AS final_score

    FROM embeddings
    JOIN deals
        ON deals.id = embeddings.deal_id

    ORDER BY final_score DESC
    LIMIT %s;
    """

    parameters = [
        pgvector,
        pgvector,
        *boost_parameters,
        limit,
    ]

    return sql, parameters


def _json_value(value):
    """Convert database date/datetime values into JSON-friendly strings."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return value


def search(query: str, limit: int = 5) -> list[dict]:
    """
    Return the best matching deals for a natural-language query.

    Semantic similarity is the primary ranking signal.
    Cuisine, location, price, and date matches provide additional
    ranking boosts rather than excluding non-matching deals.
    """

    cleaned_query = query.strip()

    if not cleaned_query:
        return []

    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")

    # Parse useful information from the query.
    parsed = parse_query(cleaned_query)

    # Convert the user's query into a BGE-M3 embedding.
    vector = get_embedding_service().embed([cleaned_query])[0]
    pgvector = vector_to_pgvector(vector)

    # Build semantic + boost ranking query.
    sql, parameters = _build_search_query(
        parsed,
        pgvector,
        limit,
    )

    # Search Supabase/PostgreSQL.
    with psycopg.connect(
        os.environ["DATABASE_URL"],
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)
            rows = cursor.fetchall()

    # Add human-readable match reasons.
    reasons = parsed.match_reasons()

    results = []

    for row in rows:
        result = {
            key: _json_value(value)
            for key, value in row.items()
        }

        result["semantic_score"] = round(
            float(result["semantic_score"]),
            4,
        )

        result["final_score"] = round(
            float(result["final_score"]),
            4,
        )

        result["match_reasons"] = reasons

        results.append(result)

    return results