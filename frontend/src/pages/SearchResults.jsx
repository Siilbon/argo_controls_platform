import { useState, useEffect } from 'react'
import DataTable from '../components/DataTable'

// One results page shared by every search (Intellution, DeltaV, ...).
// Each search is described by a config object in App.jsx.
//
// Props:
//   config   - { id, title, endpoint, searchColumns }
//                endpoint      - API path the term is appended to, e.g. '/api/deltav'
//                searchColumns - columns the API allows searching on (must match
//                                VALID_COLUMNS in the matching acp_app/api file)
//   term     - the search string
//   col      - the column to search on
//   onSearch - function called with (term, col) to run a new search
//   onBack   - function called to return to the home page
function SearchResults({ config, term, col, onSearch, onBack }) {
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  // Local copies of the form fields so typing doesn't trigger a fetch
  // until the user submits.
  const [formTerm, setFormTerm] = useState(term)
  const [formCol, setFormCol] = useState(col)

  // Runs once per search. App gives this page a key built from the search,
  // so a new search mounts a fresh copy with results reset to null.
  useEffect(() => {
    fetch(`${config.endpoint}/${encodeURIComponent(term)}?col=${encodeURIComponent(col)}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => setResults(data))
      .catch(err => setError(err.message))
  }, [config.endpoint, term, col])

  function handleSubmit(e) {
    e.preventDefault()
    if (formTerm.trim()) onSearch(formTerm.trim(), formCol)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
        <button onClick={onBack} className="text-sm text-blue-600 hover:underline">
          ← Home
        </button>
        <h1 className="text-2xl font-bold text-gray-800">{config.title} Search</h1>
      </header>

      <main className="px-6 py-6 flex flex-col gap-4">
        <form onSubmit={handleSubmit} className="flex flex-wrap gap-2">
          <input
            type="text"
            value={formTerm}
            onChange={e => setFormTerm(e.target.value)}
            className="flex-1 min-w-48 border border-gray-300 rounded-lg px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={formCol}
            onChange={e => setFormCol(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
          >
            {config.searchColumns.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm
                       hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </form>

        {error && <p className="text-red-500 text-sm">Search failed: {error}</p>}

        {results === null && !error && (
          <p className="text-gray-400 text-sm">Loading...</p>
        )}

        {results !== null && (
          <>
            <p className="text-sm text-gray-600">
              {results.total} result{results.total === 1 ? '' : 's'} for
              "<strong>{results.search_term}</strong>" in <code>{results.col}</code>
            </p>

            {results.total > 0 && (
              <DataTable
                data={results.data}
                storageKey={`${config.id}.columnVisibility`}
                exportName={`${config.id}_${results.col}_${results.search_term}`}
              />
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default SearchResults
