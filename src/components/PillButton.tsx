import type { ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost'
type Size = 'md' | 'lg'

interface PillButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
}

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: 'bg-accent text-[#0f0e0d] hover:bg-accent-light',
  secondary: 'bg-white/7 border border-border-strong text-text hover:bg-white/10',
  ghost: 'bg-black/45 text-text hover:bg-black/60',
}

const SIZE_CLASSES: Record<Size, string> = {
  md: 'px-[18px] py-3 text-sm',
  lg: 'py-4 text-[15px]',
}

export default function PillButton({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...rest
}: PillButtonProps) {
  return (
    <button
      type="button"
      className={`inline-flex items-center justify-center gap-2 rounded-full font-semibold whitespace-nowrap transition-colors disabled:opacity-60 ${VARIANT_CLASSES[variant]} ${SIZE_CLASSES[size]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  )
}
