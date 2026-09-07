# MakanRadar

Frontend for MakanRadar — a semantic search app for food deals, built from the Figma design.

## Stack

React + TypeScript + Vite + Tailwind CSS v4, with React Router (data router, for native View Transitions between pages).

## Development

```bash
npm install
npm run dev
```

## Pages

- `/` — Home (search)
- `/search` — Search results with cuisine/location filters
- `/deal/:id` — Deal detail

Deal data is currently mocked in `src/data/deals.ts`, matching the schema `{ id, restaurant, description, cuisine, location, discount, price, start_date, expiry_date, promo_code, source, source_url }`. Match scoring (`src/data/matching.ts`) is a client-side stand-in for a future backend semantic-search call.
