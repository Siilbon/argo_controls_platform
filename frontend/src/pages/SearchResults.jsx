import { useState, useEffect } from 'react'
import DataTable from '../components/DataTable'
import DataAge from '../components/DataAge'
import { fetchJson } from '../api'

// One results page shared by every search (Intellution, DeltaV, Aspen, ...).
// Each search is described by a config object in searches.js.
//
// Props:
//   config   - { id, title, endpoint, dataset, defaultColumn, searchColumns, tables }
//                endpoint      - API path the term is appended to, e.g. '/api/deltav'
//                dataset       - optional /api/datasets key; shows when the data was loaded
//                searchColumns - columns the API allows searching on (must match
//                                the allowed columns in the matching acp_app/api file)
//                tables        - optional, for searches over several tables (Aspen):
//                                [{ id, label, endpoint, defaultColumn, searchColumns,
//                                   trendTag }], shown as a table picker.
//                                trendTag(row) returns the tag to trend for a row.
//   table    - id of the chosen table, when config has tables
//   term     - the search string; empty shows just the form (opened from the nav bar)
//   col      - the column to search on
//   onSearch - function called with (term, col, table) to run a new search
//   onTrend  - function called with a tag to trend it
function SearchResults({ config, table, term, col, onSearch, onTrend }) {
  // A search without tables behaves like a single table: the config itself
  const tables = config.tables ?? [config]
  const findTable = id => tables.find(t => t.id === id) ?? tables[0]
  const active = findTable(table)
  // Separate saved column choices and CSV names per table
  const scopeId = active === config ? config.id : `${config.id}_${active.id}`

  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  // Local copies of the form fields so typing doesn't trigger a fetch
  // until the user submits.
  const [formTerm, setFormTerm] = useState(term)
  const [formCol, setFormCol] = useState(col)
  const [formTable, setFormTable] = useState(active.id)

  // Runs once per search. App gives this page a key built from the search,
  // so a new search mounts a fresh copy with results reset to null.
  useEffect(() => {
    if (!term) return
    // The API explains bad requests and connection problems in `error`
    fetchJson(`${active.endpoint}/${encodeURIComponent(term)}?col=${encodeURIComponent(col)}`)
      .then(data => setResults(data))
      .catch(err => setError(err.message))
  }, [active.endpoint, term, col])

  function handleTableChange(id) {
    setFormTable(id)
    // Columns differ between tables, so start from the new table's default
    setFormCol(findTable(id).defaultColumn)
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (formTerm.trim()) onSearch(formTerm.trim(), formCol, formTable)
  }

  const selectClass =
    'border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 text-sm ' +
    'bg-white dark:bg-gray-800 dark:text-gray-100'

  const rowAction = active.trendTag && onTrend
    ? { label: 'Trend', onClick: row => onTrend(active.trendTag(row)) }
    : null

  return (
    <main className="py-6 flex flex-col gap-4">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{config.title} Search</h1>
          {config.dataset && <DataAge dataset={config.dataset} />}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-wrap gap-2">
          {tables.length > 1 && (
            <select value={formTable} onChange={e => handleTableChange(e.target.value)} className={selectClass}>
              {tables.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
            </select>
          )}
          <input
            type="text"
            autoFocus={!term}
            value={formTerm}
            onChange={e => setFormTerm(e.target.value)}
            className="flex-1 min-w-48 border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 text-sm
                       bg-white dark:bg-gray-800 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select value={formCol} onChange={e => setFormCol(e.target.value)} className={selectClass}>
            {findTable(formTable).searchColumns.map(c => <option key={c} value={c}>{c}</option>)}
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

        {term && results === null && !error && (
          <p className="text-gray-400 dark:text-gray-500 text-sm">Loading...</p>
        )}

        {results !== null && (
          <>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {results.total} result{results.total === 1 ? '' : 's'} for
              "<strong>{results.search_term}</strong>" in <code>{results.col}</code>
              {tables.length > 1 && <> of <code>{active.label}</code></>}
            </p>

            {results.truncated && (
              <p className="text-sm text-amber-700 dark:text-amber-400">
                Showing the first {results.max_rows.toLocaleString()} matches. Narrow the search to see the rest.
              </p>
            )}

            {results.total > 0 && (
              <DataTable
                data={results.data}
                storageKey={`${scopeId}.columnVisibility`}
                exportName={`${scopeId}_${results.col}_${results.search_term}`}
                rowAction={rowAction}
              />
            )}
          </>
        )}
    </main>
  )
}

export default SearchResults
