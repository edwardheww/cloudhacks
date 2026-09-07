"""Lightweight, deterministic parsing for food-deal search constraints."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta


CUISINE_ALIASES = {
    "Chinese": ["chinese", "dim sum", "dimsum", "hotpot", "hot pot"],
    "Japanese": ["japanese", "sushi", "ramen", "udon", "donburi", "izakaya"],
    "Korean": ["korean", "kbbq", "k-bbq", "kimchi"],
    "Thai": ["thai", "tom yum", "pad thai"],
    "Italian": ["italian", "pizza", "pasta"],
    "Indian": ["indian", "curry", "biryani", "naan"],
    "Western": ["western", "steak", "burger", "burgers"],
    "Taiwanese": ["taiwanese", "bubble tea", "boba"],
    "Malay": ["malay", "nasi lemak", "mee rebus"],
    "Mexican": ["mexican", "tacos", "taco", "burrito"],
    "Mediterranean": ["mediterranean", "kebab"],
    "Singaporean": ["singaporean", "local", "hawker"],
    "Seafood": ["seafood", "fish", "prawns", "prawn", "crab"],
    "Vegetarian": ["vegetarian", "veggie", "plant based", "plant-based"],
    "Dessert": ["dessert", "cake", "ice cream", "gelato"],
    "Cafe": ["cafe", "coffee", "brunch"],
}


LOCATION_ALIASES = {
    "Bugis": ["bugis"],
    "Buona Vista": ["buona vista"],
    "Chinatown": ["chinatown"],
    "Clementi": ["clementi"],
    "Jurong East": ["jurong east", "je"],
    "Jurong West": ["jurong west", "jw"],
    "Orchard": ["orchard"],
    "Paya Lebar": ["paya lebar"],
    "Tampines": ["tampines"],
    "Tanjong Pagar": ["tanjong pagar", "tj pagar", "tp"],
    "Tiong Bahru": ["tiong bahru", "tiong baru"],
    "Holland Village": ["holland village", "holland v", "holland"],
    "Bukit Timah": ["bukit timah"],
    "Bukit Batok": ["bukit batok"],
    "Queenstown": ["queenstown"],
    "Novena": ["novena"],
    "Toa Payoh": ["toa payoh"],
    "Bishan": ["bishan"],
    "Ang Mo Kio": ["ang mo kio", "amk"],
    "Serangoon": ["serangoon"],
    "Hougang": ["hougang"],
    "Bedok": ["bedok"],
    "Katong": ["katong"],
    "East Coast": ["east coast"],
    "Little India": ["little india"],
    "Raffles Place": ["raffles place"],
    "City Hall": ["city hall"],
    "Somerset": ["somerset"],
}

CUISINES = tuple(CUISINE_ALIASES.keys())
LOCATIONS = tuple(LOCATION_ALIASES.keys())


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date
    label: str


@dataclass(frozen=True)
class ParsedQuery:
    cuisine: str | None = None
    location: str | None = None
    price: str | None = None
    date_range: DateRange | None = None


def _contains_term(query: str, term: str) -> bool:
    return (
        re.search(
            rf"(?<!\w){re.escape(term.lower())}(?!\w)",
            query,
        )
        is not None
    )


def _parse_date_range(
    query: str,
    reference_date: date,
) -> DateRange | None:

    if _contains_term(query, "today"):
        return DateRange(
            reference_date,
            reference_date,
            "today",
        )

    if _contains_term(query, "tomorrow"):
        tomorrow = reference_date + timedelta(days=1)

        return DateRange(
            tomorrow,
            tomorrow,
            "tomorrow",
        )

    if "this weekend" in query or _contains_term(query, "weekend"):
        days_until_saturday = (
            5 - reference_date.weekday()
        ) % 7

        saturday = (
            reference_date
            + timedelta(days=days_until_saturday)
        )

        return DateRange(
            saturday,
            saturday + timedelta(days=1),
            "this weekend",
        )

    if "next week" in query:
        next_monday = reference_date + timedelta(
            days=(7 - reference_date.weekday())
        )

        return DateRange(
            next_monday,
            next_monday + timedelta(days=6),
            "next week",
        )

    if "this month" in query:
        next_month = (
            reference_date.replace(day=28)
            + timedelta(days=4)
        ).replace(day=1)

        return DateRange(
            reference_date.replace(day=1),
            next_month - timedelta(days=1),
            "this month",
        )

    return None


def parse_query(
    query: str,
    reference_date: date | None = None,
) -> ParsedQuery:

    """Extract the MVP's explicit cuisine, location, price, and date filters."""

    normalized = query.casefold()
    reference_date = reference_date or date.today()

    # Cuisine
    cuisine = None

    for name, aliases in CUISINE_ALIASES.items():
        if any(
            _contains_term(normalized, alias)
            for alias in aliases
        ):
            cuisine = name
            break

    # Location
    location = None

    for name, aliases in LOCATION_ALIASES.items():
        if any(
            _contains_term(normalized, alias)
            for alias in aliases
        ):
            location = name
            break

    # Price
    price = None

    price_match = re.search(
        r"(?:under|below|less than|up to|max(?:imum)?(?: of)?)"
        r"\s*\$?\s*(\d+(?:\.\d+)?)",
        normalized,
    )

    if price_match:
        price = f"under_{price_match.group(1)}"

    elif any(
        term in normalized
        for term in (
            "cheap",
            "affordable",
            "budget",
            "low cost",
            "low-cost",
        )
    ):
        price = "cheap"

    elif any(
        term in normalized
        for term in (
            "moderate",
            "mid-range",
            "mid range",
        )
    ):
        price = "moderate"

    return ParsedQuery(
        cuisine=cuisine,
        location=location,
        price=price,
        date_range=_parse_date_range(
            normalized,
            reference_date,
        ),
    )
