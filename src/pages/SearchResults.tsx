import { MagnifyingGlassIcon } from '@heroicons/react/24/solid'
import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import DealCard from '../components/DealCard'
import MultiSelectDropdown from '../components/MultiSelectDropdown'
import PillButton from '../components/PillButton'
import TopNav from '../components/TopNav'
import Wordmark from '../components/Wordmark'
import { deals } from '../data/deals'
import { matchDeals } from '../data/matching'

export default function SearchResults() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') ?? 'cheap Thai food near Clementi')
  const [favorites, setFavorites] = useState<string[]>([])

  const cuisines = useMemo(() => Array.from(new Set(deals.map((d) => d.cuisine))), [])
  const locations = useMemo(() => Array.from(new Set(deals.map((d) => d.location))), [])

  const [activeCuisines, setActiveCuisines] = useState<string[]>(cuisines)
  const [activeLocations, setActiveLocations] = useState<string[]>(locations)

  const toggleFavorite = (id: string) => {
    setFavorites((prev) => (prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]))
  }

  const results = useMemo(
    () =>
      matchDeals(deals, query).filter(
        ({ deal }) => activeCuisines.includes(deal.cuisine) && activeLocations.includes(deal.location),
      ),
    [query, activeCuisines, activeLocations],
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
              className="min-w-0 flex-1 bg-transparent text-sm font-medium text-text focus:outline-none"
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
            {results.length} deal{results.length === 1 ? '' : 's'} found
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

        {results.length > 0 ? (
          <div className="flex flex-wrap gap-6">
            {results.map(({ deal, match }) => (
              <DealCard
                key={deal.id}
                deal={deal}
                match={match}
                query={query}
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
