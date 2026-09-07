interface LoadingBurgerProps {
  label?: string
}

export default function LoadingBurger({ label = 'Loading…' }: LoadingBurgerProps) {
  return (
    <div className="flex flex-col items-center gap-5 py-16" role="status" aria-live="polite">
      <svg viewBox="0 0 220 170" width="160" height="124" aria-hidden="true" className="-rotate-3">
        <defs>
          <filter id="crayon-wobble" x="-30%" y="-30%" width="160%" height="160%">
            <feTurbulence type="fractalNoise" baseFrequency="0.012 0.05" numOctaves="2" seed="4" result="noise" />
            <feDisplacementMap
              in="SourceGraphic"
              in2="noise"
              scale="7"
              xChannelSelector="R"
              yChannelSelector="G"
              result="wobbled"
            />
            {/* sticker-style outline: dilate the wobbled silhouette, flood
                it dark, then sit that behind the artwork so a thick
                hand-drawn border traces the whole outer shape at once
                instead of just each layer's own stroke. */}
            <feMorphology in="wobbled" operator="dilate" radius="5" result="dilated" />
            <feFlood floodColor="#160a02" result="outlineColor" />
            <feComposite in="outlineColor" in2="dilated" operator="in" result="outline" />
            <feMerge>
              <feMergeNode in="outline" />
              <feMergeNode in="wobbled" />
            </feMerge>
          </filter>

          <mask id="burger-bite-mask">
            <rect x="0" y="0" width="220" height="170" fill="white" />
            {/* each bite is two offset, differently-sized circles so the
                chomp reads as an irregular chunk rather than a neat scoop */}
            <circle className="burger-bite burger-bite-1a" cx="182" cy="44" r="0" fill="black" />
            <circle className="burger-bite burger-bite-1b" cx="168" cy="52" r="0" fill="black" />

            <circle className="burger-bite burger-bite-2a" cx="192" cy="100" r="0" fill="black" />
            <circle className="burger-bite burger-bite-2b" cx="172" cy="110" r="0" fill="black" />

            <circle className="burger-bite burger-bite-3a" cx="178" cy="142" r="0" fill="black" />
            <circle className="burger-bite burger-bite-3b" cx="164" cy="136" r="0" fill="black" />
          </mask>
        </defs>

        <g mask="url(#burger-bite-mask)" filter="url(#crayon-wobble)" stroke="#3a2314" strokeWidth="4" strokeLinejoin="round">
          {/* top bun */}
          <path d="M28 78 Q32 22 110 20 Q188 22 192 78 Z" fill="#e3a458" />
          <ellipse cx="70" cy="42" rx="4" ry="2" fill="#fff3d9" stroke="none" transform="rotate(-20 70 42)" />
          <ellipse cx="95" cy="32" rx="4" ry="2" fill="#fff3d9" stroke="none" transform="rotate(5 95 32)" />
          <ellipse cx="122" cy="30" rx="4" ry="2" fill="#fff3d9" stroke="none" transform="rotate(-8 122 30)" />
          <ellipse cx="148" cy="36" rx="4" ry="2" fill="#fff3d9" stroke="none" transform="rotate(15 148 36)" />
          <ellipse cx="108" cy="48" rx="4" ry="2" fill="#fff3d9" stroke="none" transform="rotate(-3 108 48)" />

          {/* lettuce */}
          <path
            d="M26 80 Q40 68 54 80 Q68 68 82 80 Q96 68 110 80 Q124 68 138 80 Q152 68 166 80 Q180 68 194 80 L194 94 L26 94 Z"
            fill="#7dc158"
          />

          {/* cheese */}
          <path
            d="M28 92 L192 92 L192 100 L172 112 L152 100 L132 112 L112 100 L92 112 L72 100 L52 112 L32 100 Z"
            fill="#f3c344"
          />

          {/* patty */}
          <rect x="26" y="108" width="168" height="24" rx="10" fill="#6b3d24" />

          {/* bottom bun */}
          <path
            d="M30 132 L190 132 Q196 132 196 140 L196 148 Q196 158 186 158 L34 158 Q24 158 24 148 L24 140 Q24 132 30 132 Z"
            fill="#dd9a52"
          />
        </g>

        <g className="burger-crumbs" filter="url(#crayon-wobble)" stroke="#3a2314" strokeWidth="1.5">
          <circle className="burger-crumb burger-crumb-1" cx="196" cy="48" r="3.4" fill="#caa06a" />
          <circle className="burger-crumb burger-crumb-2" cx="205" cy="58" r="2" fill="#8c5a2e" />
          <circle className="burger-crumb burger-crumb-3" cx="203" cy="100" r="4" fill="#e3a458" />
          <circle className="burger-crumb burger-crumb-4" cx="212" cy="112" r="2.4" fill="#6b3d24" />
          <circle className="burger-crumb burger-crumb-5" cx="195" cy="140" r="3" fill="#dd9a52" />
          <circle className="burger-crumb burger-crumb-6" cx="204" cy="150" r="2" fill="#caa06a" />
        </g>
      </svg>

      <p className="text-sm text-text-muted">{label}</p>
    </div>
  )
}
