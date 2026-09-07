"""
One-off backfill: replace deals.image_url with a Pexels photo chosen from a
food-specific search query built from each deal's restaurant name, title,
and cuisine. Run once (or re-run to refresh); the frontend just reads the
stored URL afterwards, no API calls at request time.

Usage: backend/.venv/bin/python3 scripts/apply_pexels_images.py
Requires PEXELS_API_KEY in backend/.env.
"""

import os
import re
import time
from pathlib import Path

import psycopg
import requests
from dotenv import load_dotenv
from psycopg.rows import dict_row

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

API_KEY = os.environ["PEXELS_API_KEY"]
SEARCH_URL = "https://api.pexels.com/v1/search"

# Specific dish/food words worth searching for directly — checked against
# both the restaurant name and the deal title before falling back to cuisine.
STRONG_FOOD_WORDS = [
    "sashimi", "sushi", "ramen", "udon", "soba", "katsu", "tempura",
    "dumpling", "dumplings", "xiaolongbao", "dimsum", "dim sum", "wonton",
    "bbq", "grill", "steak", "roast", "duck", "chicken rice", "hainanese",
    "char siu", "wok", "noodle", "noodles", "bibimbap", "kimchi", "bulgogi",
    "hotpot", "hot pot", "pad thai", "tom yum", "curry", "tandoori",
    "biryani", "naan", "thali", "masala", "pizza", "pasta", "burger",
    "taco", "burrito", "laksa", "nasi lemak", "satay", "bak kut teh",
    "chicken", "fish", "seafood", "prawn", "salmon", "beef", "pork",
    "dessert", "cake", "matcha", "bubble tea", "coffee", "brunch",
    "pancake", "waffle", "bento", "donburi", "nigiri", "maki", "izakaya",
    "vegetarian", "salad", "soup", "porridge", "congee", "hokkien mee",
]


def find_food_word(text: str) -> str | None:
    text = text.lower()
    for word in STRONG_FOOD_WORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            return word
    return None


def build_query(restaurant: str, title: str, cuisine: str) -> str:
    word = find_food_word(restaurant) or find_food_word(title)
    if word:
        return f"{word} food dish"
    return f"{cuisine} food dish"


def search_pexels(query: str) -> str | None:
    resp = requests.get(
        SEARCH_URL,
        headers={"Authorization": API_KEY},
        params={"query": query, "per_page": 1, "orientation": "landscape"},
        timeout=15,
    )
    if resp.status_code == 429:
        print("  rate limited, sleeping 60s...")
        time.sleep(60)
        return search_pexels(query)
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        return None
    return photos[0]["src"]["large"]


def main():
    connection = psycopg.connect(
        os.environ["DATABASE_URL"], connect_timeout=10, prepare_threshold=None, row_factory=dict_row
    )
    with connection.cursor() as cur:
        cur.execute("SELECT id, restaurant, title, cuisine FROM deals ORDER BY id;")
        deals = cur.fetchall()

    print(f"Processing {len(deals)} deals...")
    updates = []
    specific_count = 0
    fallback_count = 0
    miss_count = 0

    for deal in deals:
        deal_id, restaurant, title, cuisine = (
            deal["id"], deal["restaurant"], deal["title"], deal["cuisine"],
        )
        word = find_food_word(restaurant) or find_food_word(title)
        query = build_query(restaurant, title, cuisine)
        url = search_pexels(query)

        tier = "specific" if word else "cuisine-fallback"
        if not url:
            # last-resort: just the cuisine name
            url = search_pexels(f"{cuisine} food")
            tier = "generic-fallback"

        if not url:
            miss_count += 1
            print(f"  {deal_id} {restaurant:<24} [MISS] query={query!r}")
            continue

        if tier == "specific":
            specific_count += 1
        elif tier == "cuisine-fallback":
            fallback_count += 1
        else:
            fallback_count += 1

        print(f"  {deal_id} {restaurant:<24} [{tier}] {url}")
        updates.append((deal_id, url))
        time.sleep(0.3)  # stay comfortably under 200 req/hour

    with connection.cursor() as cur:
        for deal_id, url in updates:
            cur.execute("UPDATE deals SET image_url = %s WHERE id = %s", (url, deal_id))
        connection.commit()
    connection.close()

    print(f"\nSummary: specific={specific_count} fallback={fallback_count} miss={miss_count}")
    print(f"Wrote {len(updates)}/{len(deals)} image URLs.")


if __name__ == "__main__":
    main()
