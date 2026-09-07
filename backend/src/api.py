"""HTTP layer over search_engine — the FastAPI app the frontend calls.

Run from the backend directory:
    uvicorn src.api:app --reload --port 8000
"""

from __future__ import annotations

import logging

import psycopg
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.query_parser import CUISINES, LOCATIONS
from src.search_engine import get_deal, get_embedding_service, list_deals, search

logger = logging.getLogger(__name__)

app = FastAPI(title="MakanRadar API")


@app.on_event("startup")
def warm_up_embedding_model() -> None:
    # BGE-M3's first load sets up its (CPU) inference pool. Doing that here,
    # on the main thread during startup, avoids a hang/deadlock that occurs
    # when it instead happens lazily inside a request's worker thread.
    get_embedding_service().embed(["warm up"])

app.add_middleware(
    CORSMiddleware,
    # Vite picks the next free port (5173, 5174, ...) when one is taken, so
    # match any local dev port rather than hardcoding one. Cloudflare Pages
    # deployments (production + preview branches) live under *.pages.dev.
    allow_origin_regex=r"^(http://(localhost|127\.0\.0\.1):\d+|https://[a-z0-9-]+\.pages\.dev)$",
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/filters")
def get_filters() -> dict:
    return {"cuisines": list(CUISINES), "locations": list(LOCATIONS)}


@app.get("/api/search")
def search_deals(q: str = Query(""), limit: int = Query(10, ge=1, le=20)) -> list[dict]:
    # search() already treats a blank/whitespace query as "no results" —
    # accept it here too rather than rejecting it as a validation error.
    try:
        return search(q, limit=limit)
    except psycopg.OperationalError:
        logger.exception("Database connection failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from None


@app.get("/api/deals")
def get_all_deals(limit: int = Query(20, ge=1, le=100)) -> list[dict]:
    try:
        return list_deals(limit=limit)
    except psycopg.OperationalError:
        logger.exception("Database connection failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from None


@app.get("/api/deals/{deal_id}")
def get_deal_by_id(deal_id: str) -> dict:
    try:
        deal = get_deal(deal_id)
    except psycopg.OperationalError:
        logger.exception("Database connection failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal
