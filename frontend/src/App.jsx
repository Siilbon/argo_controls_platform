import { useState, useEffect } from 'react'
import { Link, Route, Routes, useNavigate, useParams, useSearchParams } from 'react-router'
import Home from './pages/Home'
import SearchResults from './pages/SearchResults'
import Trend from './pages/Trend'
import Gcc from './pages/Gcc'
import NodeIds from './pages/NodeIds'
import Status from './pages/Status'
import NavBar from './components/NavBar'
import Footer from './components/Footer'
import { SEARCHES, NAV_LINKS } from './searches'
import { fetchJson, trendUrl } from './api'

// 'dark' or 'light': the saved choice, or the system setting if there isn't one
function getInitialTheme() {
  try {
    const saved = localStorage.getItem('theme')
    if (saved === 'dark' || saved === 'light') return saved
  } catch {
    // Storage can be blocked (private window); fall back to the system setting
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// /search/:searchId?q=term&col=column&table=table
// The URL holds the whole search, so links and the back button work.
function SearchPage() {
  const { searchId } = useParams()
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const config = SEARCHES[searchId]
  if (!config) return <NotFound />

  const tables = config.tables
  const table = tables ? (tables.find(t => t.id === params.get('table')) ?? tables[0]) : config
  const term = params.get('q') ?? ''
  const col = params.get('col') ?? table.defaultColumn

  function search(newTerm, newCol, newTable) {
    setParams({ q: newTerm, col: newCol, ...(tables ? { table: newTable } : {}) })
  }

  return (
    <SearchResults
      // A new key makes React throw away the old page and start fresh
      key={`${searchId}:${table.id}:${col}:${term}`}
      config={config}
      table={tables ? table.id : undefined}
      term={term}
      col={col}
      onSearch={search}
      onTrend={tag => navigate(trendUrl(tag))}
    />
  )
}

// /gcc?eos=21
function GccPage() {
  const [params] = useSearchParams()
  const eosType = params.get('eos') ?? undefined
  // Keyed so a new EOS type from the home page resets the form
  return <Gcc key={eosType ?? ''} eosType={eosType} />
}

// /nodeid?tags=FT1,TT2&field=IP_INPUT_VALUE&raw=0
function NodeIdsPage() {
  const [params] = useSearchParams()
  // Keyed so Back/Forward or a new lookup resets the form to match the URL
  return <NodeIds key={params.toString()} />
}

function NotFound() {
  return (
    <main className="py-6 flex flex-col gap-2">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Page not found</h1>
      <Link to="/" className="text-blue-600 dark:text-blue-400 hover:underline">Back to home</Link>
    </main>
  )
}

function App() {
  const [theme, setTheme] = useState(getInitialTheme)
  // Signed-in account from IIS Windows Authentication, shown in the nav bar
  const [user, setUser] = useState(null)

  // Tailwind's dark: classes key off the "dark" class on <html>
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  useEffect(() => {
    fetchJson('/api/me').then(data => setUser(data.user)).catch(() => setUser(null))
  }, [])

  function toggleTheme() {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    try {
      localStorage.setItem('theme', next)
    } catch {
      // Storage can be blocked; the theme just won't be remembered
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">
      <NavBar links={NAV_LINKS} user={user} theme={theme} onToggleTheme={toggleTheme} />
      {/* flex-1 pushes the footer to the bottom on short pages. The shared max
          width and side padding live here, so pages don't set their own.
          min-w-0 lets wide tables scroll inside their box instead of widening the page. */}
      <div className="flex-1 w-full min-w-0 max-w-7xl mx-auto px-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search/:searchId" element={<SearchPage />} />
          <Route path="/trend" element={<Trend theme={theme} />} />
          <Route path="/gcc" element={<GccPage />} />
          <Route path="/nodeid" element={<NodeIdsPage />} />
          <Route path="/status" element={<Status user={user} />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <Footer />
    </div>
  )
}

export default App
