import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import { Copy } from 'lucide-react'
import DataTable from '../components/DataTable'
import { fetchJson, splitTags } from '../api'

const DEFAULT_FIELD = 'IP_INPUT_VALUE'

const inputClass =
  'w-full border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 text-sm ' +
  'bg-white dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 ' +
  'focus:outline-none focus:ring-2 focus:ring-blue-500'
const labelClass = 'text-sm text-gray-600 dark:text-gray-400'
const buttonClass =
  'bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors disabled:opacity-50'
const cardClass =
  'bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 flex flex-col gap-4'

// OPC UA node IDs that IT uses to read Aspen through IoTHub.
// The lookup lives in the URL (/nodeid?tags=FT1,TT2&field=IP_INPUT_VALUE&raw=0),
// so a result can be bookmarked or sent to whoever asked for it.
function NodeIds() {
  const [params, setParams] = useSearchParams()
  const tags = splitTags(params.get('tags'))
  const field = params.get('field') || DEFAULT_FIELD
  const raw = params.get('raw') !== '0'
  const query = tags.length > 0
    ? new URLSearchParams({ tags: tags.join(','), field, raw: raw ? '1' : '0' }).toString()
    : null

  // Form values, started from the URL
  const [tagInput, setTagInput] = useState(tags.join('\n'))
  const [fieldInput, setFieldInput] = useState(field)
  const [rawInput, setRawInput] = useState(raw)

  // The latest finished request: { query, result, error }
  const [response, setResponse] = useState(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!query) return
    let current = true
    fetchJson(`/api/aspen/nodeid?${query}`)
      .then(result => current && setResponse({ query, result }))
      .catch(err => current && setResponse({ query, error: err.message }))
    return () => { current = false }
  }, [query])

  const loading = query && response?.query !== query
  const result = !loading && response?.result
  const error = !loading && response?.error

  function handleSubmit(e) {
    e.preventDefault()
    const newTags = splitTags(tagInput)
    if (newTags.length === 0) return
    setCopied(false)
    setParams({
      tags: newTags.join(','),
      ...(fieldInput.trim() && fieldInput.trim() !== DEFAULT_FIELD ? { field: fieldInput.trim() } : {}),
      ...(rawInput ? {} : { raw: '0' }),
    })
  }

  // Tab-separated so it pastes straight into Excel or an email
  async function copyResults() {
    const lines = result.data.map(r => `${r.tag}\t${r.node_id ?? 'not found'}`)
    try {
      await navigator.clipboard.writeText(lines.join('\n'))
      setCopied(true)
    } catch {
      // Clipboard access can be blocked; the CSV download still works
      setCopied(false)
    }
  }

  return (
    // Narrower than the data pages: this is a short form
    <main className="max-w-4xl py-6 flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">OPC UA Node IDs</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          The node IDs IT uses to read Aspen tags through IoTHub.
        </p>
      </div>

      <section className={cardClass}>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <label className="flex flex-col gap-1">
            <span className={labelClass}>Aspen tags (one per line, or separated by commas or spaces)</span>
            <textarea
              required
              autoFocus
              rows={5}
              placeholder={'e.g. FT21001\nTT21002'}
              value={tagInput}
              onChange={e => setTagInput(e.target.value)}
              className={`${inputClass} font-mono`}
            />
          </label>
          <div className="flex flex-wrap items-end gap-3">
            <label className="flex flex-col gap-1 flex-1 min-w-48">
              <span className={labelClass}>Field</span>
              <input
                type="text"
                placeholder={DEFAULT_FIELD}
                value={fieldInput}
                onChange={e => setFieldInput(e.target.value)}
                className={`${inputClass} font-mono`}
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className={labelClass}>Data access</span>
              <select
                value={rawInput ? 'raw' : 'other'}
                onChange={e => setRawInput(e.target.value === 'raw')}
                className={inputClass}
              >
                <option value="raw">Raw (ns=3)</option>
                <option value="other">Not raw (ns=2)</option>
              </select>
            </label>
            <button type="submit" disabled={loading} className={buttonClass}>
              Get node IDs
            </button>
          </div>
        </form>
      </section>

      {loading && <p className="text-gray-400 dark:text-gray-500 text-sm">Looking up {tags.length} tag(s)...</p>}
      {error && <p className="text-red-500 text-sm">Lookup failed: {error}</p>}

      {result && (
        <section className="flex flex-col gap-3">
          {result.missing.length > 0 && (
            <p className="text-sm text-amber-700 dark:text-amber-400">
              Not in Aspen: {result.missing.join(', ')}
            </p>
          )}
          <div className="flex items-center gap-3">
            <button
              onClick={copyResults}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <Copy className="w-4 h-4" aria-hidden="true" />
              Copy tags and node IDs
            </button>
            {copied && <span className="text-sm text-green-700 dark:text-green-400">Copied</span>}
          </div>
          <DataTable data={result.data} exportName={`opcua_node_ids_${result.field}`} />
        </section>
      )}
    </main>
  )
}

export default NodeIds
