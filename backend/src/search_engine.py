"""Reusable AI search engine for the future FastAPI layer."""

from __future__ import annotations

import re
import os
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from src.embedding_service import EmbeddingService, vector_to_pgvector
from src.query_parser import CUISINE_ALIASES, LOCATION_ALIASES, ParsedQuery, parse_query

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

_embedding_service: EmbeddingService | None = None
_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    """Return one shared connection pool for the lifetime of the backend process.

    Opening a fresh TCP+TLS+auth connection to Supabase on every request was
    costing ~1s per request on its own, before any query even ran. A pool
    keeps a handful of connections warm and reuses them instead.
    """
    global _pool

    if _pool is None:
        _pool = ConnectionPool(
            os.environ["DATABASE_URL"],
            min_size=1,
            max_size=5,
            kwargs={"prepare_threshold": None, "row_factory": dict_row},
        )

    return _pool

DEAL_FIELDS = """
    id, restaurant, title, cuisine, location, discount, price,
    start_date, expiry_date, promo_code, source, source_url, image_url
"""

GET_DEAL_SQL = f"SELECT {DEAL_FIELDS} FROM deals WHERE id = %s;"

LIST_DEALS_SQL = f"""
SELECT {DEAL_FIELDS} FROM deals
WHERE COALESCE(expiry_date, 'infinity'::date) >= CURRENT_DATE
ORDER BY expiry_date ASC NULLS LAST, id
LIMIT %s;
"""


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
        deals.image_url,
        deals.raw_text,

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


def _date_value(value):
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return date.fromisoformat(value)

    return None


# Words too generic to ever be worth surfacing as "why this matched" on
# their own — either filler, or words that describe the search itself
# rather than a dish (the structured cuisine/location/price/date reasons
# already cover those angles).
_KEYWORD_STOPWORDS = {
    "a", "an", "the", "for", "and", "or", "with", "near", "in", "at", "of",
    "to", "is", "are", "some", "any", "me", "im", "i", "want", "wanna",
    "looking", "craving", "find", "get", "good", "best", "nice", "food",
    "deal", "deals", "place", "places", "restaurant", "restaurants", "eat",
    "eating", "hungry", "please", "cheap", "affordable", "budget", "under",
    "below", "less", "than", "up", "max", "maximum", "today", "tomorrow",
    "weekend", "week", "month", "this", "next", "moderate",
}


def _keyword_exclusions(parsed_query: ParsedQuery) -> set[str]:
    """Words already explained by a structured reason (cuisine/location name
    or alias) shouldn't also get a redundant keyword-match chip."""
    exclude: set[str] = set()

    if parsed_query.cuisine:
        exclude.add(parsed_query.cuisine.casefold())
        exclude.update(alias.casefold() for alias in CUISINE_ALIASES.get(parsed_query.cuisine, []))

    if parsed_query.location:
        exclude.add(parsed_query.location.casefold())
        exclude.update(alias.casefold() for alias in LOCATION_ALIASES.get(parsed_query.location, []))

    return exclude


def _get_keyword_match_reason(cleaned_query: str, parsed_query: ParsedQuery, deal: dict) -> str | None:
    """Surface a reason when a specific food/dish word from the query
    literally appears in the deal's title or raw description.

    Semantic similarity already ranks dish-level matches (e.g. "fried
    chicken") correctly, but the structured reasons above only ever explain
    cuisine/location/price/date — so a genuinely strong dish match showed no
    reason at all. This closes that gap without touching the ranking itself.
    """
    exclude = _keyword_exclusions(parsed_query)

    tokens = [
        token
        for token in re.findall(r"[a-z']+", cleaned_query.casefold())
        if len(token) > 2 and token not in _KEYWORD_STOPWORDS and token not in exclude
    ]

    if not tokens:
        return None

    deal_text = " ".join(str(deal.get(field) or "") for field in ("title", "raw_text")).casefold()

    # Prefer the longest matching phrase (up to 3 words) so "fried chicken"
    # is reported as one reason rather than two separate single-word hits.
    for size in range(min(3, len(tokens)), 0, -1):
        for start in range(len(tokens) - size + 1):
            phrase = " ".join(tokens[start : start + size])

            if re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", deal_text):
                return f'Matches "{phrase}"'

    return None


def _get_match_reasons(deal, parsed_query, cleaned_query: str):
    """Explain why a deal matched the user's search."""

    reasons = []

    # Cuisine
    if parsed_query.cuisine:
        deal_cuisine = (deal.get("cuisine") or "").casefold()

        if deal_cuisine == parsed_query.cuisine.casefold():
            reasons.append(f"{parsed_query.cuisine} cuisine")

    # Location
    if parsed_query.location:
        deal_location = (deal.get("location") or "").casefold()

        if parsed_query.location.casefold() in deal_location:
            reasons.append(parsed_query.location)

    # Price
    if parsed_query.price:
        deal_price = (deal.get("price") or "").casefold()

        if parsed_query.price == "cheap":
            if deal_price == "cheap":
                reasons.append("Budget-friendly")

        elif parsed_query.price == "moderate":
            if deal_price == "moderate":
                reasons.append("Moderate price")

        elif parsed_query.price.startswith("under_"):
            max_price = float(parsed_query.price.split("_")[1])

            # Extract the first price from the deal's price field
            price_match = re.search(
                r"\$?\s*(\d+(?:\.\d+)?)",
                deal_price,
            )

            if price_match:
                actual_price = float(price_match.group(1))

                if actual_price <= max_price:
                    reasons.append(f"Under ${max_price:g}")

    # Date
    if parsed_query.date_range:
        deal_start = _date_value(deal.get("start_date"))
        deal_end = _date_value(deal.get("expiry_date"))

        if deal_start and deal_end:
            if (
                deal_start <= parsed_query.date_range.end
                and deal_end >= parsed_query.date_range.start
            ):
                reasons.append(
                    f"Available {parsed_query.date_range.label}"
                )

    # Dish/keyword-level match — the part structured reasons above can't see.
    keyword_reason = _get_keyword_match_reason(cleaned_query, parsed_query, deal)
    if keyword_reason:
        reasons.append(keyword_reason)

    return reasons

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
    with get_pool().connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)
            rows = cursor.fetchall()

    results = []

    for row in rows:
        match_reasons = _get_match_reasons(row, parsed, cleaned_query)
        result = {
            key: _json_value(value)
            for key, value in row.items()
            if key != "raw_text"
        }

        result["semantic_score"] = round(
            float(result["semantic_score"]),
            4,
        )

        result["final_score"] = round(
            float(result["final_score"]),
            4,
        )

        result["match_reasons"] = match_reasons

        results.append(result)

    return results


def list_deals(limit: int = 20) -> list[dict]:
    """Return currently-active deals with no query-dependent match info —
    used for browsing (e.g. an empty search) rather than a semantic query.

    This is the interface the FastAPI layer's `/deals` route should call.
    """
    with get_pool().connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(LIST_DEALS_SQL, (limit,))
            rows = cursor.fetchall()

    return [{key: _json_value(value) for key, value in row.items()} for row in rows]


def get_deal(deal_id: str) -> dict | None:
    """Return one deal by id, with no query-dependent match info attached.

    This is the interface the FastAPI layer's deal-detail route should call.
    """
    with get_pool().connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_DEAL_SQL, (deal_id,))
            row = cursor.fetchone()

    if row is None:
        return None
    return {key: _json_value(value) for key, value in row.items()}
