import type { Deal } from './deals'

export interface DealMatch {
  matchPercent: number
  matchReasons: string[]
}

function isCurrentlyActive(deal: Deal, today = new Date()): boolean {
  return today >= new Date(deal.start_date) && today <= new Date(deal.expiry_date)
}

// Stand-in for the backend's semantic search: once deals are served from an
// API, this is where a per-query match score + reasons come back from the
// AI matching call instead of being computed client-side.
export function matchDeal(deal: Deal, query: string): DealMatch {
  const q = query.trim().toLowerCase()
  const reasons: string[] = []
  let score = 55

  if (q && q.includes(deal.cuisine.toLowerCase())) {
    reasons.push(`Matches ${deal.cuisine} cuisine`)
    score += 20
  }

  const locationKeyword = deal.location.toLowerCase().split(' ')[0]
  if (q && q.includes(locationKeyword)) {
    reasons.push(`Located in ${deal.location}, near your search`)
    score += 15
  }

  if (isCurrentlyActive(deal)) {
    reasons.push('Currently active')
    score += 10
  }

  return {
    matchPercent: Math.min(99, score),
    matchReasons: reasons.length > 0 ? reasons : ['General match based on your search'],
  }
}

export function matchDeals(deals: Deal[], query: string): Array<{ deal: Deal; match: DealMatch }> {
  return deals
    .map((deal) => ({ deal, match: matchDeal(deal, query) }))
    .sort((a, b) => b.match.matchPercent - a.match.matchPercent)
}
