import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

DATASET_PATH = BACKEND_DIR / "data" / "mock" / "dataset.json"

UPSERT_DEAL = """
INSERT INTO deals (
    id, raw_text, restaurant, title, cuisine, location,
    discount, price, start_date, expiry_date,
    promo_code, source, source_url
)
VALUES (
    %(id)s, %(raw_text)s, %(restaurant)s, %(title)s, %(cuisine)s,
    %(location)s, %(discount)s, %(price)s, %(start_date)s,
    %(expiry_date)s, %(promo_code)s, %(source)s, %(source_url)s
)
ON CONFLICT (id) DO UPDATE SET
    raw_text = EXCLUDED.raw_text,
    restaurant = EXCLUDED.restaurant,
    title = EXCLUDED.title,
    cuisine = EXCLUDED.cuisine,
    location = EXCLUDED.location,
    discount = EXCLUDED.discount,
    price = EXCLUDED.price,
    start_date = EXCLUDED.start_date,
    expiry_date = EXCLUDED.expiry_date,
    promo_code = EXCLUDED.promo_code,
    source = EXCLUDED.source,
    source_url = EXCLUDED.source_url;
"""

def main():
    with DATASET_PATH.open(encoding="utf-8") as file:
        deals = json.load(file)

    with psycopg.connect(os.environ["DATABASE_URL"],connect_timeout=10,prepare_threshold=None) as connection:
        with connection.cursor() as cursor:
            for deal in deals:
                cursor.execute(UPSERT_DEAL, deal)
        connection.commit()

    print(f"Loaded {len(deals)} deals into Supabase.")

if __name__ == "__main__":
    main()