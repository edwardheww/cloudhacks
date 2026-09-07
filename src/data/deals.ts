export interface Deal {
  id: string
  restaurant: string
  description: string
  cuisine: string
  location: string
  discount: string
  price: string
  start_date: string
  expiry_date: string
  promo_code: string
  source: string
  source_url: string
}

export const deals: Deal[] = [
  {
    id: 'thai-express',
    restaurant: 'Thai Express',
    description: '20% off lunch sets',
    cuisine: 'Thai',
    location: 'Clementi Mall',
    discount: '20% off',
    price: '$6.90',
    start_date: '2026-09-01',
    expiry_date: '2026-09-15',
    promo_code: 'THAI20',
    source: 'Telegram',
    source_url: 'https://t.me/sgfoodiedeals/4821',
  },
  {
    id: 'soi-thai',
    restaurant: 'Soi Thai',
    description: '$10 lunch special',
    cuisine: 'Thai',
    location: 'Clementi',
    discount: '$10 flat',
    price: '$10.00',
    start_date: '2026-09-05',
    expiry_date: '2026-09-08',
    promo_code: 'SOI10',
    source: 'Telegram',
    source_url: 'https://t.me/sgfoodiedeals/4835',
  },
  {
    id: 'sushi-express',
    restaurant: 'Sushi Express',
    description: '1-for-1 sushi rolls',
    cuisine: 'Japanese',
    location: 'Clementi Ave 2',
    discount: '1-for-1',
    price: '$14.90',
    start_date: '2026-09-01',
    expiry_date: '2026-09-20',
    promo_code: 'SUSHI11',
    source: 'Telegram',
    source_url: 'https://t.me/sgfoodiedeals/4802',
  },
]

export function getDeal(id: string): Deal | undefined {
  return deals.find((deal) => deal.id === id)
}
