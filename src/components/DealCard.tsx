import { CheckIcon, HeartIcon, MapPinIcon, PhotoIcon, SparklesIcon } from '@heroicons/react/24/solid'
import { HeartIcon as HeartIconOutline } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'
import type { Deal } from '../api/deals'
import { capitalize, formatShortDate } from '../lib/format'
import Chip from './Chip'
import PillButton from './PillButton'

interface DealMatchInfo {
  matchPercent: number
  matchReasons: string[]
}

interface DealCardProps {
  deal: Deal
  match: DealMatchInfo | null
  query: string
  favorited: boolean
  onToggleFavorite: (id: string) => void
}

export default function DealCard({ deal, match, query, favorited, onToggleFavorite }: DealCardProps) {
  const directionsHref = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(deal.location)}`

  return (
    <div className="flex w-full max-w-[440px] flex-col overflow-hidden rounded-[20px] border border-white/6 bg-surface">
      <div className="relative h-[260px] w-full bg-hero">
        <div className="absolute inset-0 bg-gradient-to-b from-black/0 to-black/75" />

        {match && (
          <div className="absolute top-3.5 right-3.5 flex items-center gap-1 rounded-full bg-black/45 px-2.5 py-1.5 text-xs font-semibold">
            <SparklesIcon className="size-3.5 text-accent-light" />
            {Math.round(match.matchPercent)}% match
          </div>
        )}

        <button
          type="button"
          onClick={() => onToggleFavorite(deal.id)}
          aria-pressed={favorited}
          aria-label={favorited ? 'Remove from favorites' : 'Add to favorites'}
          className="absolute top-3.5 left-3.5 rounded-full bg-black/45 p-2"
        >
          {favorited ? (
            <HeartIcon className="size-4 text-accent" />
          ) : (
            <HeartIconOutline className="size-4 text-text" />
          )}
        </button>

        <div className="absolute inset-x-0 top-[90px] flex flex-col items-center gap-1.5 text-[rgba(255,255,255,0.55)]">
          <PhotoIcon className="size-7 opacity-50" />
          <span className="text-xs">Food photo placeholder</span>
        </div>

        <div className="absolute bottom-[24px] left-[18px] flex flex-col gap-1">
          <p className="text-[19px] font-bold text-text">{deal.restaurant}</p>
          <p className="text-[13px] font-medium text-white/75">{deal.title}</p>
        </div>
      </div>

      <div className="flex w-full flex-col gap-4 p-[18px]">
        <div className="flex w-full flex-wrap gap-x-5 gap-y-2.5">
          <div className="flex flex-col gap-[3px]">
            <p className="text-[11px] text-text-muted">Location</p>
            <p className="flex items-center gap-1 text-[13px] font-semibold">
              <MapPinIcon className="size-3.5 text-accent" />
              {deal.location}
            </p>
          </div>
          <div className="flex flex-col gap-[3px]">
            <p className="text-[11px] text-text-muted">Price</p>
            <p className="text-[13px] font-semibold">
              {capitalize(deal.price)}
              {deal.discount && <span className="font-normal text-text-muted"> · {deal.discount}</span>}
            </p>
          </div>
          <div className="flex flex-col gap-[3px]">
            <p className="text-[11px] text-text-muted">Valid until</p>
            <p className="text-[13px] font-semibold">{formatShortDate(deal.expiry_date)}</p>
          </div>
          <div className="flex flex-col gap-[3px]">
            <p className="text-[11px] text-text-muted">Source</p>
            <p className="text-[13px] font-semibold">{deal.source}</p>
          </div>
        </div>

        {match && (
          <div className="flex flex-wrap gap-x-2 gap-y-1.5">
            {match.matchReasons.slice(0, 3).map((reason) => (
              <Chip key={reason} tone="success">
                <span className="inline-flex items-center gap-1">
                  <CheckIcon className="size-3" />
                  {reason}
                </span>
              </Chip>
            ))}
          </div>
        )}

        <div className="flex w-full gap-2.5">
          <Link to={`/deal/${deal.id}`} state={{ query }} viewTransition className="flex-1">
            <PillButton variant="primary" className="w-full">
              View Deal
            </PillButton>
          </Link>
          <a href={directionsHref} target="_blank" rel="noopener noreferrer">
            <PillButton variant="secondary">
              <MapPinIcon className="size-3.5" />
              Directions
            </PillButton>
          </a>
        </div>
      </div>
    </div>
  )
}
