import { FireIcon, MagnifyingGlassIcon, MicrophoneIcon } from '@heroicons/react/24/solid'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Chip from '../components/Chip'
import PillButton from '../components/PillButton'
import TopNav from '../components/TopNav'
import Wordmark, { WORDMARK_TYPE_DURATION_MS } from '../components/Wordmark'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'

const SUGGESTIONS = ['coffee near NUS', '1-for-1 sushi', 'Thai food this weekend']

const WORDMARK_START_DELAY = 250
// Everything except the logo fades in together, right after it finishes typing.
const REST_DELAY = WORDMARK_START_DELAY + WORDMARK_TYPE_DURATION_MS + 200

export default function Home() {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  const goSearch = (value: string) => {
    const trimmed = value.trim()
    const path = trimmed ? `/search?q=${encodeURIComponent(trimmed)}` : '/search'
    navigate(path, { viewTransition: true })
  }

  const speech = useSpeechRecognition((transcript) => {
    setQuery(transcript)
    goSearch(transcript)
  })

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-hero px-4 py-20 sm:px-6 sm:py-24">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-black/10 via-black/35 to-black/85" />

      <div className="relative z-10 flex w-full max-w-[720px] flex-col items-center gap-6 text-center sm:gap-8">
        <div
          className="fade-in-up inline-flex items-center gap-1.5 rounded-full border border-white/15 bg-white/8 px-3.5 py-2 text-[13px] font-semibold"
          style={{ animationDelay: `${REST_DELAY}ms` }}
        >
          <FireIcon className="size-3.5 text-accent" />8 new deals this weekend
        </div>

        <Wordmark size="hero" animated startDelayMs={WORDMARK_START_DELAY} />

        <p
          className="fade-in-up max-w-[600px] text-base text-text-dim sm:text-[19px]"
          style={{ animationDelay: `${REST_DELAY}ms` }}
        >
          Find food deals without the digging.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            goSearch(query)
          }}
          className="fade-in-up flex w-full max-w-[560px] items-center gap-2 rounded-full border border-white/14 bg-white/6 py-1.5 pr-1.5 pl-4 shadow-[0px_8px_30px_0px_rgba(0,0,0,0.4)] sm:gap-3 sm:pl-6"
          style={{ animationDelay: `${REST_DELAY}ms` }}
        >
          <MagnifyingGlassIcon className="size-4 text-text-dim" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What are you craving?"
            className="min-w-0 flex-1 bg-transparent py-3 text-[15px] text-text-dim placeholder:text-text-dim focus:outline-none"
          />
          {speech.supported && (
            <button
              type="button"
              onClick={() => (speech.listening ? speech.stop() : speech.start())}
              aria-label={speech.listening ? 'Stop voice search' : 'Search by voice'}
              aria-pressed={speech.listening}
              className={`flex size-9 shrink-0 items-center justify-center rounded-full transition-colors ${
                speech.listening ? 'animate-pulse bg-accent text-[#0f0e0d]' : 'bg-white/8 text-text-dim hover:bg-white/14'
              }`}
            >
              <MicrophoneIcon className="size-4" />
            </button>
          )}
          <PillButton type="submit" variant="primary">
            Search
          </PillButton>
        </form>

        <div
          className="fade-in-up flex w-full flex-wrap items-center justify-center gap-2.5"
          style={{ animationDelay: `${REST_DELAY}ms` }}
        >
          {SUGGESTIONS.map((suggestion) => (
            <Chip key={suggestion} onClick={() => goSearch(suggestion)}>
              {suggestion}
            </Chip>
          ))}
        </div>
      </div>

      <TopNav animated delayMs={REST_DELAY} />
    </div>
  )
}
