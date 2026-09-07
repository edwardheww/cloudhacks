import {
  ArrowLeftIcon,
  CalendarDaysIcon,
  CheckIcon,
  CurrencyDollarIcon,
  MapPinIcon,
  PhotoIcon,
  SparklesIcon,
  TagIcon,
} from '@heroicons/react/24/solid'
import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { getDeal, searchDeals, type Deal } from '../api/deals'
import LoadingBurger from '../components/LoadingBurger'
import PillButton from '../components/PillButton'
import Wordmark from '../components/Wordmark'
import { capitalize, formatDateRange } from '../lib/format'

interface MatchInfo {
  matchPercent: number
  matchReasons: string[]
}

export default function DealDetail() {
  const { id } = useParams<{ id: string }>()
  const location = useLocation()
  const state = location.state as { query?: string; match?: MatchInfo } | null
  const query = state?.query ?? ''
  const passedMatch = state?.match ?? null

  const [deal, setDeal] = useState<Deal | null>(null)
  const [status, setStatus] = useState<'loading' | 'ready' | 'notfound' | 'error'>('loading')
  const [match, setMatch] = useState<MatchInfo | null>(passedMatch)
  const [copied, setCopied] = useState(false)
  const [imageFailed, setImageFailed] = useState(false)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    setStatus('loading')

    getDeal(id)
      .then((d) => {
        if (cancelled) return
        setDeal(d)
        setStatus(d ? 'ready' : 'notfound')
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })

    // The card that linked here already computed this deal's match — reuse
    // it instead of re-running a full semantic search (a second BGE-M3
    // embedding + DB round trip) just to recover the same numbers. Only
    // fall back to re-fetching when arriving without that context (a
    // direct link, refresh, or bookmark).
    if (passedMatch) {
      setMatch(passedMatch)
    } else if (query.trim()) {
      searchDeals(query, 20)
        .then((results) => {
          if (cancelled) return
          const hit = results.find((r) => r.id === id)
          if (hit) {
            setMatch({ matchPercent: Math.min(100, hit.final_score * 100), matchReasons: hit.match_reasons })
          }
        })
        .catch(() => {
          // match context is a bonus — silently skip if it fails
        })
    } else {
      setMatch(null)
    }

    return () => {
      cancelled = true
    }
  }, [id, query, passedMatch])

  if (status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg">
        <LoadingBurger label="Loading deal…" />
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-bg text-center">
        <p className="text-lg text-text">Couldn't reach the search service.</p>
        <Link to="/search" className="text-accent underline">
          Back to results
        </Link>
      </div>
    )
  }

  if (status === 'notfound' || !deal) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-bg text-center">
        <p className="text-lg text-text">Deal not found.</p>
        <Link to="/search" className="text-accent underline">
          Back to results
        </Link>
      </div>
    )
  }

  const directionsHref = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(deal.location)}`
  const showImage = deal.image_url && !imageFailed

  const handleGetDeal = async () => {
    if (!deal.promo_code) return
    try {
      await navigator.clipboard.writeText(deal.promo_code)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // clipboard unavailable — ignore
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center bg-bg">
      <div className="relative flex h-[360px] w-full flex-col justify-end overflow-hidden bg-hero px-4 pb-6 sm:h-[480px] sm:px-14 sm:pb-9">
        {showImage && (
          <img
            src={deal.image_url ?? undefined}
            alt=""
            className="absolute inset-0 size-full object-cover"
            onError={() => setImageFailed(true)}
          />
        )}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-black/25 via-black/30 to-black/90" />

        <div className="relative z-10 flex flex-col gap-3 pt-4 sm:contents">
          <div className="flex items-center justify-between gap-3 sm:contents">
            <Link to="/" aria-label="MakanRadar home" className="sm:absolute sm:top-6 sm:left-14">
              <Wordmark size="header" />
            </Link>

            {match && (
              <div className="flex shrink-0 items-center gap-1.5 rounded-full bg-black/45 px-3 py-2 text-xs font-semibold sm:absolute sm:top-8 sm:right-14 sm:px-4 sm:py-2.5 sm:text-[13px]">
                <SparklesIcon className="size-4 text-accent-light" />
                {Math.round(match.matchPercent)}% overall match
              </div>
            )}
          </div>

          <Link
            to={query.trim() ? `/search?q=${encodeURIComponent(query)}` : '/search'}
            viewTransition
            className="inline-flex w-fit items-center gap-1.5 rounded-full bg-black/45 px-4 py-2.5 text-[13px] font-semibold sm:absolute sm:top-[39px] sm:left-[158px]"
          >
            <ArrowLeftIcon className="size-3.5" />
            Back to results
          </Link>
        </div>

        <div
          className={`absolute inset-x-0 top-[70px] flex flex-col items-center gap-2 text-[rgba(255,255,255,0.55)] sm:top-[110px] ${showImage ? 'hidden' : ''}`}
        >
          <PhotoIcon className="size-9 opacity-50" />
          <span className="text-sm">Food photo placeholder</span>
        </div>

        <div className="relative z-10 flex flex-col gap-2">
          <h1 className="text-[28px] font-black text-text sm:text-[44px]">{deal.restaurant}</h1>
          <p className="text-base font-semibold text-accent-light sm:text-lg">{deal.title}</p>
        </div>
      </div>

      <main className="flex w-full max-w-[1440px] flex-col px-4 pt-8 pb-16 sm:px-14 sm:pt-10">
        <div className="flex w-full flex-col gap-8 lg:flex-row lg:gap-12">
          <div className="flex min-w-0 flex-1 flex-col gap-7">
            <div className="flex flex-wrap items-center gap-6">
              <span className="flex items-center gap-1.5 text-sm font-medium text-text-muted">
                <MapPinIcon className="size-4 text-accent" />
                {deal.location}
              </span>
              <span className="flex items-center gap-1.5 text-sm font-medium text-text-muted">
                <CalendarDaysIcon className="size-4" />
                {formatDateRange(deal.start_date, deal.expiry_date)}
              </span>
              <span className="flex items-center gap-1.5 text-sm font-medium text-text-muted">
                <CurrencyDollarIcon className="size-4" />
                {capitalize(deal.price)}
              </span>
              {deal.discount && (
                <span className="flex items-center gap-1.5 text-sm font-medium text-text-muted">
                  <TagIcon className="size-4" />
                  {deal.discount}
                </span>
              )}
            </div>

            {deal.promo_code && (
              <div className="inline-flex w-fit items-center gap-2.5 rounded-full border border-border-strong bg-white/6 px-[18px] py-3.5">
                <span className="text-[13px] font-medium text-text-muted">Promo Code</span>
                <span className="text-sm font-bold text-text">{deal.promo_code}</span>
              </div>
            )}

            {match && (
              <div className="flex flex-col gap-3.5">
                <p className="text-xl font-bold text-text">Why this matched</p>
                {match.matchReasons.map((reason) => (
                  <div
                    key={reason}
                    className="flex items-center gap-2.5 rounded-[14px] bg-surface-soft px-[18px] py-3.5 text-sm"
                  >
                    <CheckIcon className="size-4 shrink-0 text-success" />
                    <span className="font-medium text-text">{reason}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex w-full shrink-0 flex-col gap-5 lg:w-[420px]">
            <div className="flex flex-col gap-2.5">
              <PillButton variant="primary" size="lg" className="w-full" onClick={handleGetDeal}>
                {copied ? `Copied ${deal.promo_code}!` : deal.promo_code ? 'Get This Deal' : 'No Code Needed'}
              </PillButton>
              <a href={directionsHref} target="_blank" rel="noopener noreferrer">
                <PillButton variant="secondary" size="lg" className="w-full">
                  <MapPinIcon className="size-4" />
                  Get Directions
                </PillButton>
              </a>
            </div>

            <div className="flex flex-col gap-3.5 rounded-[18px] border border-white/6 bg-surface p-[22px]">
              <p className="text-[15px] font-bold text-text">Original promotion</p>
              <div className="flex items-center gap-2.5">
                <p className="flex-1 text-[13px] text-text-muted">Source: {deal.source}</p>
                <a href={deal.source_url} target="_blank" rel="noopener noreferrer">
                  <PillButton variant="secondary" className="bg-white/8 border-none px-4 py-2.5 text-xs">
                    View Original
                  </PillButton>
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
