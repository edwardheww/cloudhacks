# MakanRadar backend

Semantic search API over food deals: BGE-M3 embeddings + pgvector (Supabase Postgres) + FastAPI.

## Setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # pulls in torch + FlagEmbedding — several hundred MB
cp .env.example .env                        # fill in DATABASE_URL
```

Data is already loaded into Supabase for this project (`scripts/load_deals.py` / `scripts/generate_embeddings.py`
are only needed again if the dataset or embeddings change).

## Run

```bash
.venv/bin/uvicorn src.api:app --reload --port 8000
```

The BGE-M3 model downloads on first run (a few minutes) and is then cached under `~/.cache/huggingface`.
Startup deliberately warms the model up (on the main thread) before accepting requests — doing that lazily
inside a request's worker thread was observed to hang indefinitely (a threading/multiprocessing interaction
in FlagEmbedding's inference pool), so don't remove `warm_up_embedding_model()` in `src/api.py`.

Once running, subsequent searches are fast (sub-second) since the model and connection stay warm.

## Endpoints

- `GET /api/search?q=<query>&limit=<n>` — semantic search, returns deals with `semantic_score` + `match_reasons`
- `GET /api/deals/{id}` — a single deal, no query-dependent fields
- `GET /api/filters` — the cuisine/location vocabulary the query parser recognizes (for filter UI)

CORS is open to any `localhost`/`127.0.0.1` port, matching Vite's dev server.

## Frontend

The frontend (`../src`) talks to this API via `src/api/deals.ts`, defaulting to `http://localhost:8000`.
Override with `VITE_API_BASE` if running the backend elsewhere.
