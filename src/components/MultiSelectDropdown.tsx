import { ChevronDownIcon } from '@heroicons/react/24/solid'
import { useEffect, useRef, useState } from 'react'

interface MultiSelectDropdownProps {
  label: string
  options: string[]
  selected: string[]
  onChange: (next: string[]) => void
}

export default function MultiSelectDropdown({ label, options, selected, onChange }: MultiSelectDropdownProps) {
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

  const toggleOption = (value: string) => {
    onChange(selected.includes(value) ? selected.filter((v) => v !== value) : [...selected, value])
  }

  const summary =
    selected.length === 0
      ? 'None'
      : selected.length === options.length
        ? 'All'
        : selected.length === 1
          ? selected[0]
          : `${selected.length} selected`

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="inline-flex items-center gap-2 rounded-full border border-[#47403b] bg-white/6 px-3 py-[7px] text-xs font-medium text-text transition-colors hover:bg-white/10"
      >
        <span className="text-text-muted">{label}:</span>
        {summary}
        <ChevronDownIcon className={`size-3 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <div className="absolute top-full left-0 z-10 mt-2 flex w-52 flex-col overflow-hidden rounded-2xl border border-white/8 bg-[#1a1714] py-2 shadow-[0px_10px_30px_0px_rgba(0,0,0,0.5)]">
          <div className="flex items-center justify-between px-4 pb-2 text-[11px] text-text-muted">
            <button type="button" className="hover:text-text" onClick={() => onChange(options)}>
              Select all
            </button>
            <button type="button" className="hover:text-text" onClick={() => onChange([])}>
              Clear
            </button>
          </div>

          {options.map((option) => {
            const checked = selected.includes(option)
            return (
              <label
                key={option}
                className="flex cursor-pointer items-center gap-3 px-4 py-2.5 text-sm text-text transition-colors hover:bg-white/5"
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleOption(option)}
                  className="size-4 shrink-0 accent-accent"
                />
                {option}
              </label>
            )
          })}
        </div>
      )}
    </div>
  )
}
