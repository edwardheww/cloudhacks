import type { CSSProperties } from 'react'

const LETTER_ROTATIONS = [6, -4, 6, -5, 4, -5, 4, -6, 3, -4]
const LINES = ['Makan', 'Radar']
const LETTER_COUNT = LINES.join('').length
const LETTER_STEP_MS = 90

// Time from the first letter starting to the last letter appearing — use
// this to schedule whatever comes after the wordmark finishes typing in.
export const WORDMARK_TYPE_DURATION_MS = (LETTER_COUNT - 1) * LETTER_STEP_MS + 40

const SIZE_CLASSES = {
  hero: 'text-[100px] leading-[0.82]',
  header: 'text-[32px] leading-[0.82]',
} as const

interface WordmarkProps {
  size?: keyof typeof SIZE_CLASSES
  className?: string
  /** Type the wordmark in letter-by-letter, terminal-style, instead of rendering it statically. */
  animated?: boolean
  /** Delay before the first letter starts typing in (ms). Only used when animated. */
  startDelayMs?: number
}

export default function Wordmark({
  size = 'header',
  className = '',
  animated = false,
  startDelayMs = 0,
}: WordmarkProps) {
  let letterIndex = 0

  return (
    <div
      role="img"
      aria-label="MakanRadar"
      className={`wordmark-transition flex flex-col items-center font-wordmark text-text ${SIZE_CLASSES[size]} ${className}`}
    >
      {LINES.map((line, lineIndex) => {
        const isLastLine = lineIndex === LINES.length - 1

        return (
          <div key={line} className="flex items-end">
            {line.split('').map((letter, i) => {
              const rotation = LETTER_ROTATIONS[letterIndex % LETTER_ROTATIONS.length]
              const delay = startDelayMs + letterIndex * LETTER_STEP_MS
              letterIndex += 1

              const style: CSSProperties = {
                display: 'inline-block',
                marginLeft: i === 0 ? 0 : '-0.05em',
                transform: `rotate(${rotation}deg)`,
                ...(animated ? { animationDelay: `${delay}ms` } : {}),
              }

              return (
                <span
                  key={i}
                  style={style}
                  aria-hidden="true"
                  className={animated ? 'letter-type-in' : ''}
                >
                  {letter}
                </span>
              )
            })}

            {animated && isLastLine && (
              <span
                aria-hidden="true"
                className="terminal-cursor mb-[0.08em] ml-[0.05em] inline-block h-[0.78em] w-[0.12em] bg-text"
                style={{ animationDelay: `${startDelayMs + LETTER_COUNT * LETTER_STEP_MS}ms` }}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
