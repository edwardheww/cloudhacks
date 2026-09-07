"""Run a semantic-search query against embeddings stored in Supabase.

Example:
    python scripts/search_deals.py "cheap Thai food near Clementi"
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.query_parser import parse_query
from src.search_engine import search


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python scripts/search_deals.py "your food query"')

    query = " ".join(sys.argv[1:])
    parsed = parse_query(query)
    results = search(query)
    reasons = ", ".join(parsed.match_reasons()) or "no explicit filters"
    print(f"Detected filters: {reasons}")
    for result in results:
        score = float(result.pop("semantic_score"))
        print(f"{score:.1%} | {result['restaurant']} | {result['title']} | {result['location']}")


if __name__ == "__main__":
    main()
