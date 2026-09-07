export interface Deal {
  id: string
  restaurant: string
  title: string
  cuisine: string
  location: string
  discount: string | null
  price: string
  start_date: string
  expiry_date: string
  promo_code: string | null
  source: string
  source_url: string
  image_url: string | null
}

export interface SearchResult extends Deal {
  semantic_score: number
  final_score: number
  match_reasons: string[]
}

export interface Filters {
  cuisines: string[]
  locations: string[]
}

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

/**
 * In-memory, key-based cache for GET requests within this page session.
 * Callers get an in-flight or already-resolved promise back — concurrent
 * calls with the same key share one request, and a failure evicts the key
 * so the next call retries instead of caching the error.
 */
function cached<T>(cache: Map<string, Promise<T>>, key: string, fetcher: () => Promise<T>): Promise<T> {
  let entry = cache.get(key)
  if (!entry) {
    entry = fetcher().catch((error: unknown) => {
      cache.delete(key)
      throw error
    })
    cache.set(key, entry)
  }
  return entry
}

async function fetchJson<T>(url: string, errorLabel: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`${errorLabel} (${res.status})`)
  }
  return res.json()
}

// A search/browse result only changes if the underlying data does, which
// doesn't happen within a session — so caching by query avoids re-running a
// full semantic search (a BGE-M3 embedding + DB round trip) every time the
// same search is revisited, e.g. clicking "Back to results" from a deal.
const searchCache = new Map<string, Promise<SearchResult[]>>()
const listCache = new Map<string, Promise<Deal[]>>()
let filtersCache: Promise<Filters> | null = null

export function searchDeals(query: string, limit = 20): Promise<SearchResult[]> {
  return cached(searchCache, `${query}::${limit}`, () =>
    fetchJson(`${API_BASE}/api/search?q=${encodeURIComponent(query)}&limit=${limit}`, 'Search failed'),
  )
}

export function listDeals(limit = 20): Promise<Deal[]> {
  return cached(listCache, String(limit), () => fetchJson(`${API_BASE}/api/deals?limit=${limit}`, 'Failed to load deals'))
}

export async function getDeal(id: string): Promise<Deal | null> {
  const res = await fetch(`${API_BASE}/api/deals/${encodeURIComponent(id)}`)
  if (res.status === 404) return null
  if (!res.ok) {
    throw new Error(`Failed to load deal (${res.status})`)
  }
  return res.json()
}

// The cuisine/location vocabulary is static for the lifetime of the app —
// cache it too, for the same reason.
export function getFilters(): Promise<Filters> {
  if (!filtersCache) {
    filtersCache = fetchJson<Filters>(`${API_BASE}/api/filters`, 'Failed to load filters').catch((error: unknown) => {
      filtersCache = null
      throw error
    })
  }
  return filtersCache
}
