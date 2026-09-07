export function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

export function formatDateRange(startIso: string, expiryIso: string): string {
  return `${formatShortDate(startIso)} – ${formatShortDate(expiryIso)}`
}
