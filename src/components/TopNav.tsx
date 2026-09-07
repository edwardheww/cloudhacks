import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const ITEMS = [
  { label: 'Home', to: '/' },
  { label: 'Search', to: '/search' },
] as const

interface TopNavProps {
  animated?: boolean
  delayMs?: number
  /** 'fixed' overlays the page (for screens with no header row, e.g. Home).
   *  'inline' sits as a normal flex item inside an existing header. */
  variant?: 'fixed' | 'inline'
}

export default function TopNav({ animated = false, delayMs = 0, variant = 'fixed' }: TopNavProps) {
  const { pathname } = useLocation()
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handleClickOutside = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])

  const positionClass = variant === 'fixed' ? 'fixed top-8 right-8' : 'relative shrink-0'

  return (
    <div
      ref={rootRef}
      className={`${positionClass} z-20 ${animated ? 'fade-in-up' : ''}`}
      style={animated ? { animationDelay: `${delayMs}ms` } : undefined}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label="Toggle navigation menu"
        className="flex flex-col items-center justify-center gap-[5px] rounded-full border border-white/8 bg-[#1a1714] p-3.5 shadow-[0px_10px_30px_0px_rgba(0,0,0,0.5)]"
      >
        <span className="h-0.5 w-5 rounded-full bg-text" />
        <span className="h-0.5 w-5 rounded-full bg-text" />
        <span className="h-0.5 w-5 rounded-full bg-text" />
      </button>

      {open && (
        <div className="absolute top-full right-0 mt-2 flex w-44 flex-col overflow-hidden rounded-2xl border border-white/8 bg-[#1a1714] py-2 shadow-[0px_10px_30px_0px_rgba(0,0,0,0.5)]">
          {ITEMS.map(({ label, to }) => {
            const isActive = to !== null && pathname === to
            const className = `px-5 py-3 text-left text-sm font-medium transition-colors ${
              isActive ? 'text-accent' : 'text-white/70 hover:bg-white/5 hover:text-white'
            }`
            return to ? (
              <Link
                key={label}
                to={to}
                viewTransition={to !== '/'}
                className={className}
                onClick={() => setOpen(false)}
              >
                {label}
              </Link>
            ) : (
              <span key={label} className={`${className} cursor-default`}>
                {label}
              </span>
            )
          })}
        </div>
      )}
    </div>
  )
}
