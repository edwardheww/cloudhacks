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
}

export interface SearchResult extends Deal {
  semantic_score: number
  match_reasons: string[]
}

export interface Filters {
  cuisines: string[]
  locations: string[]
}

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export async function searchDeals(query: string, limit = 20): Promise<SearchResult[]> {
  const url = `${API_BASE}/api/search?q=${encodeURIComponent(query)}&limit=${limit}`
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`Search failed (${res.status})`)
  }
  return res.json()
}

export async function listDeals(limit = 20): Promise<Deal[]> {
  const res = await fetch(`${API_BASE}/api/deals?limit=${limit}`)
  if (!res.ok) {
    throw new Error(`Failed to load deals (${res.status})`)
  }
  return res.json()
}

export async function getDeal(id: string): Promise<Deal | null> {
  const res = await fetch(`${API_BASE}/api/deals/${encodeURIComponent(id)}`)
  if (res.status === 404) return null
  if (!res.ok) {
    throw new Error(`Failed to load deal (${res.status})`)
  }
  return res.json()
}

export async function getFilters(): Promise<Filters> {
  const res = await fetch(`${API_BASE}/api/filters`)
  if (!res.ok) {
    throw new Error(`Failed to load filters (${res.status})`)
  }
  return res.json()
}
