import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import DealDetail from './pages/DealDetail'
import Home from './pages/Home'
import SearchResults from './pages/SearchResults'

// A data router (rather than plain <BrowserRouter>/<Routes>) is required for
// the `viewTransition` navigation option to actually trigger
// `document.startViewTransition`.
const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/search', element: <SearchResults /> },
  { path: '/deal/:id', element: <DealDetail /> },
])

export default function App() {
  return <RouterProvider router={router} />
}
