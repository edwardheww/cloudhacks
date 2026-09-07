"""Lightweight, deterministic parsing for food-deal search constraints."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta

CUISINES = ("Chinese", "Japanese", "Thai")
LOCATIONS = (
    "Bugis",
    "Buona Vista",
    "Chinatown",
    "Clementi",
    "Jurong East",
    "Orchard",
    "Paya Lebar",
    "Tampines",
    "Tanjong Pagar",
    "Tiong Bahru",
)


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

    def match_reasons(self) -> list[str]:
        reasons = []
        if self.cuisine:
            reasons.append(self.cuisine)
        if self.location:
            reasons.append(self.location)
        if self.price:
            reasons.append(self.price.title())
        if self.date_range:
            reasons.append(self.date_range.label.title())
        return reasons


def _contains_term(query: str, term: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(term.lower())}(?!\w)", query) is not None


def _parse_date_range(query: str, reference_date: date) -> DateRange | None:
    if _contains_term(query, "today"):
        return DateRange(reference_date, reference_date, "today")

    if _contains_term(query, "tomorrow"):
        tomorrow = reference_date + timedelta(days=1)
        return DateRange(tomorrow, tomorrow, "tomorrow")

    if "this weekend" in query or _contains_term(query, "weekend"):
        # Monday=0 ... Saturday=5. "This weekend" means the next Sat-Sun;
        # when run during a weekend, it means that current weekend.
        days_until_saturday = (5 - reference_date.weekday()) % 7
        saturday = reference_date + timedelta(days=days_until_saturday)
        return DateRange(saturday, saturday + timedelta(days=1), "this weekend")

    if "next week" in query:
        next_monday = reference_date + timedelta(days=(7 - reference_date.weekday()))
        return DateRange(next_monday, next_monday + timedelta(days=6), "next week")

    if "this month" in query:
        next_month = (reference_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        return DateRange(reference_date.replace(day=1), next_month - timedelta(days=1), "this month")

    return None


def parse_query(query: str, reference_date: date | None = None) -> ParsedQuery:
    """Extract the MVP's explicit cuisine, location, price, and date filters."""
    normalized = query.casefold()
    reference_date = reference_date or date.today()

    cuisine = next((item for item in CUISINES if _contains_term(normalized, item)), None)
    location = next((item for item in LOCATIONS if _contains_term(normalized, item)), None)

    price = None
    if any(term in normalized for term in ("cheap", "affordable", "budget", "low cost", "low-cost")):
        price = "cheap"
    elif any(term in normalized for term in ("moderate", "mid-range", "mid range")):
        price = "moderate"

    return ParsedQuery(
        cuisine=cuisine,
        location=location,
        price=price,
        date_range=_parse_date_range(normalized, reference_date),
    )
