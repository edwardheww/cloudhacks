import { MagnifyingGlassIcon } from '@heroicons/react/24/solid'
import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getFilters, listDeals, searchDeals, type Deal } from '../api/deals'
import DealCard from '../components/DealCard'
import MultiSelectDropdown from '../components/MultiSelectDropdown'
import PillButton from '../components/PillButton'
import TopNav from '../components/TopNav'
import Wordmark from '../components/Wordmark'

interface MatchInfo {
  matchPercent: number
  matchReasons: string[]
}

interface ResultRow {
  deal: Deal
  match: MatchInfo | null
}

export default function SearchResults() {
  const [searchParams, setSearchParams] = useSearchParams()
  const submittedQuery = searchParams.get('q') ?? ''
  const isBrowsing = !submittedQuery.trim()
  const [query, setQuery] = useState(submittedQuery)
  const [favorites, setFavorites] = useState<string[]>([])

  const [cuisines, setCuisines] = useState<string[]>([])
  const [locations, setLocations] = useState<string[]>([])
  const [activeCuisines, setActiveCuisines] = useState<string[]>([])
  const [activeLocations, setActiveLocations] = useState<string[]>([])

  const [rows, setRows] = useState<ResultRow[]>([])
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')

  useEffect(() => {
    getFilters()
      .then((f) => {
        setCuisines(f.cuisines)
        setLocations(f.locations)
        setActiveCuisines(f.cuisines)
        setActiveLocations(f.locations)
      })
      .catch(() => {
        // filter vocabulary is a nice-to-have; leave dropdowns empty on failure
      })
  }, [])

  useEffect(() => {
    let cancelled = false
    setStatus('loading')

    const request = isBrowsing
      ? listDeals().then((deals) => deals.map((deal) => ({ deal, match: null })))
      : searchDeals(submittedQuery).then((results) =>
          results.map((result) => ({
            deal: result,
            match: { matchPercent: result.semantic_score * 100, matchReasons: result.match_reasons },
          })),
        )

    request
      .then((r) => {
        if (cancelled) return
        setRows(r)
        setStatus('ready')
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [submittedQuery, isBrowsing])

  const toggleFavorite = (id: string) => {
    setFavorites((prev) => (prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]))
  }

  const filteredRows = useMemo(
    () => rows.filter((r) => activeCuisines.includes(r.deal.cuisine) && activeLocations.includes(r.deal.location)),
    [rows, activeCuisines, activeLocations],
  )

  return (
    <div className="flex min-h-screen flex-col items-center bg-bg">
      <header className="flex w-full items-center gap-10 border-b border-white/8 px-14 py-6">
        <Link to="/" aria-label="MakanRadar home">
          <Wordmark size="header" />
        </Link>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            setSearchParams(query ? { q: query } : {})
          }}
          className="flex flex-1 items-center gap-10"
        >
          <div className="flex flex-1 items-center gap-2.5 rounded-full border border-white/10 bg-white/6 px-[18px] py-3">
            <MagnifyingGlassIcon className="size-3.5 text-text-muted" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="cheap Thai food near Clementi"
              className="min-w-0 flex-1 bg-transparent text-sm font-medium text-text placeholder:text-text-muted focus:outline-none"
            />
          </div>
          <PillButton type="submit" variant="primary">
            Search
          </PillButton>
        </form>

        <TopNav variant="inline" />
      </header>

      <main className="flex w-full max-w-[1440px] flex-1 flex-col gap-6 px-14 pt-10 pb-16">
        <div className="flex flex-wrap items-center gap-4">
          <p className="text-[22px] font-bold text-text">
            {status === 'loading'
              ? 'Searching…'
              : isBrowsing
                ? 'Showing all deals'
                : `${filteredRows.length} deal${filteredRows.length === 1 ? '' : 's'} found`}
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <MultiSelectDropdown
              label="Cuisine"
              options={cuisines}
              selected={activeCuisines}
              onChange={setActiveCuisines}
            />
            <MultiSelectDropdown
              label="Location"
              options={locations}
              selected={activeLocations}
              onChange={setActiveLocations}
            />
          </div>
        </div>

        {status === 'error' ? (
          <p className="py-16 text-center text-text-muted">
            Couldn't reach the search service. Is the backend running?
          </p>
        ) : status === 'loading' ? (
          <p className="py-16 text-center text-text-muted">Searching for deals…</p>
        ) : filteredRows.length > 0 ? (
          <div className="flex flex-wrap gap-6">
            {filteredRows.map(({ deal, match }) => (
              <DealCard
                key={deal.id}
                deal={deal}
                match={match}
                query={submittedQuery}
                favorited={favorites.includes(deal.id)}
                onToggleFavorite={toggleFavorite}
              />
            ))}
          </div>
        ) : (
          <p className="py-16 text-center text-text-muted">
            No deals match your filters. Try clearing a filter above.
          </p>
        )}
      </main>
    </div>
  )
}
