import { CheckIcon, SparklesIcon } from '@heroicons/react/24/solid'
import Chip from './Chip'

interface MatchReasonsProps {
  reasons: string[]
  variant?: 'card' | 'detail'
}

export default function MatchReasons({ reasons, variant = 'card' }: MatchReasonsProps) {
  const visibleReasons = reasons.filter(Boolean)

  if (visibleReasons.length === 0) {
    return null
  }

  if (variant === 'detail') {
    return (
      <section className="flex flex-col gap-3.5">
        <p className="flex items-center gap-2 text-xl font-bold text-text">
          <SparklesIcon className="size-5 text-accent-light" />
          Why this matched
        </p>
        <div className="grid gap-2.5 sm:grid-cols-2">
          {visibleReasons.map((reason) => (
            <div
              key={reason}
              className="flex min-w-0 items-center gap-2.5 rounded-[14px] bg-surface-soft px-[18px] py-3.5 text-sm"
            >
              <CheckIcon className="size-4 shrink-0 text-success" />
              <span className="min-w-0 font-medium text-text">{reason}</span>
            </div>
          ))}
        </div>
      </section>
    )
  }

  return (
    <div className="flex flex-col gap-2 rounded-[14px] border border-white/6 bg-white/[0.035] px-3.5 py-3">
      <p className="flex items-center gap-1.5 text-[11px] font-semibold text-text-muted">
        <SparklesIcon className="size-3.5 text-accent-light" />
        Why this matched
      </p>
      <div className="flex flex-wrap gap-x-2 gap-y-1.5">
        {visibleReasons.map((reason) => (
          <Chip key={reason} tone="success">
            <span className="inline-flex min-w-0 items-center gap-1">
              <CheckIcon className="size-3 shrink-0" />
              {reason}
            </span>
          </Chip>
        ))}
      </div>
    </div>
  )
}
