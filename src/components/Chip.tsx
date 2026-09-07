interface ChipProps {
  children: React.ReactNode
  active?: boolean
  onClick?: () => void
  tone?: 'default' | 'success'
}

export default function Chip({ children, active = true, onClick, tone = 'default' }: ChipProps) {
  const toneClasses =
    tone === 'success'
      ? 'bg-white/5 text-success'
      : active
        ? 'bg-white/6 border border-[#47403b] text-text'
        : 'bg-transparent border border-white/10 text-text-muted'

  const Component = onClick ? 'button' : 'div'

  return (
    <Component
      onClick={onClick}
      type={onClick ? 'button' : undefined}
      className={`inline-flex items-center rounded-full px-3 py-[7px] text-xs font-medium whitespace-nowrap transition-colors ${toneClasses} ${onClick ? 'cursor-pointer hover:bg-white/10' : ''}`}
    >
      {children}
    </Component>
  )
}
