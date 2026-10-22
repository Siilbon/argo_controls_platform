import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router'
import { RefreshCw, X } from 'lucide-react'
import { fetchJson, rememberTrendQuery, splitTags } from '../api'

// Quick time ranges; 'custom' shows start/end pickers instead
const RANGES = [
  { id: '1', label: 'Last hour' },
  { id: '8', label: 'Last 8 hours' },
  { id: '24', label: 'Last 24 hours' },
  { id: '168', label: 'Last 7 days' },
  { id: '720', label: 'Last 30 days' },
  { id: 'custom', label: 'Custom' },
]

function buildQuery(tags, range, start, end) {
  const params = new URLSearchParams()
  tags.forEach(tag => params.append('tags', tag))
  if (range === 'custom') {
    params.set('start', start)
    params.set('end', end)
  } else {
    params.set('hours', range)
  }
  return params.toString()
}

// Plotly traces and layout for the trend response.
// stacked gives each tag its own y axis in a row, sharing the time axis.
function buildFigure(trend, stacked, theme) {
  const dark = theme === 'dark'
  const textColor = dark ? '#e5e7eb' : '#374151'
  const gridColor = dark ? '#374151' : '#e5e7eb'
  const axisStyle = { gridcolor: gridColor, zerolinecolor: gridColor, automargin: true }
  const count = trend.series.length

  const traces = trend.series.map((s, i) => {
    const textValues = s.values.some(v => typeof v === 'string')
    return {
      type: 'scatter',
      mode: 'lines',
      name: s.tag,
      x: trend.ts,
      y: s.values,
      // Discrete states step between values instead of sloping
      line: { width: 1.5, shape: textValues ? 'hv' : 'linear' },
      yaxis: stacked && i > 0 ? `y${i + 1}` : 'y',
    }
  })

  const layout = {
    autosize: true,
    height: stacked ? Math.max(420, 180 * count) : 520,
    margin: { t: 30, r: 20, b: 40, l: 60 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: textColor, size: 12 },
    hovermode: 'x unified',
    // Plotly's hover box defaults to a white background, so set it per theme
    hoverlabel: {
      bgcolor: dark ? '#1f2937' : '#ffffff',
      bordercolor: dark ? '#4b5563' : '#d1d5db',
      font: { color: dark ? '#f3f4f6' : '#111827' },
    },
    showlegend: true,
    legend: { orientation: 'h', y: 1.08 },
    xaxis: { ...axisStyle, type: 'date' },
    yaxis: axisStyle,
  }

  if (stacked) {
    layout.grid = { rows: count, columns: 1, pattern: 'coupled', ygap: 0.15 }
    trend.series.forEach((s, i) => {
      const key = i === 0 ? 'yaxis' : `yaxis${i + 1}`
      layout[key] = { ...axisStyle, title: { text: s.tag } }
    })
  }

  return { traces, layout }
}

// Trend settings live in the URL (/trend?tags=FT1,TT2&range=8&stacked=1), so a
// trend can be bookmarked, shared, or linked from a notification.
//
// Props:
//   theme - 'light' or 'dark', so the chart matches the page
function Trend({ theme }) {
  const [params, setParams] = useSearchParams()
  const tags = splitTags(params.get('tags'))
  const range = RANGES.some(r => r.id === params.get('range')) ? params.get('range') : '8'
  const start = params.get('start') ?? ''
  const end = params.get('end') ?? ''
  const stacked = params.get('stacked') === '1'

  // Change some settings in the URL. Adding or removing tags gets its own
  // history entry so Back undoes it; other tweaks replace the current entry.
  function update(changes, { newEntry = false } = {}) {
    setParams(current => {
      const next = new URLSearchParams(current)
      for (const [key, value] of Object.entries(changes)) {
        if (value === '' || value === null || value === false) next.delete(key)
        else next.set(key, value === true ? '1' : value)
      }
      return next
    }, { replace: !newEntry })
  }
  const setTags = newTags => update({ tags: newTags.join(',') }, { newEntry: true })

  // Tags added from a search join this trend (see trendUrl in api.js)
  const paramString = params.toString()
  useEffect(() => { rememberTrendQuery(paramString) }, [paramString])

  const [tagInput, setTagInput] = useState('')
  // Bumped by the refresh button to fetch again with the same settings
  const [refreshCount, setRefreshCount] = useState(0)

  // The latest finished request: { key, trend, error }. trend is the last good
  // result, kept on screen while a new one loads or if it fails.
  const [response, setResponse] = useState(null)

  const plotRef = useRef(null)

  const customReady = range !== 'custom' || (start && end)
  const query = tags.length > 0 && customReady ? buildQuery(tags, range, start, end) : null
  // Identifies one request; loading until a response for it comes back
  const requestKey = query && `${query}#${refreshCount}`
  const loading = Boolean(requestKey) && response?.key !== requestKey
  const trend = response?.trend ?? null
  const error = response?.key === requestKey ? response.error : null

  useEffect(() => {
    if (!requestKey) return
    // Ignore a response that arrives after the settings have changed again
    let cancelled = false
    fetchJson(`/api/aspen/trend?${query}`)
      .then(data => {
        if (!cancelled) setResponse({ key: requestKey, trend: data, error: null })
      })
      .catch(err => {
        if (!cancelled) setResponse(prev => ({ key: requestKey, trend: prev?.trend ?? null, error: err.message }))
      })
    return () => { cancelled = true }
  }, [query, requestKey])

  // Draw the chart. Plotly is large, so it's only downloaded once a trend is shown.
  useEffect(() => {
    const el = plotRef.current
    if (!el || !trend || trend.series.length === 0) return
    let cancelled = false
    import('plotly.js-dist-min').then(({ default: Plotly }) => {
      if (cancelled) return
      const { traces, layout } = buildFigure(trend, stacked, theme)
      Plotly.react(el, traces, layout, { responsive: true, displaylogo: false })
    })
    return () => { cancelled = true }
  }, [trend, stacked, theme])

  // Free Plotly's listeners when leaving the page
  useEffect(() => {
    const el = plotRef.current
    return () => {
      import('plotly.js-dist-min').then(({ default: Plotly }) => Plotly.purge(el))
    }
  }, [])

  function addTags(e) {
    e.preventDefault()
    const added = splitTags(tagInput).filter(t => !tags.includes(t))
    if (added.length) setTags([...tags, ...added])
    setTagInput('')
  }

  const inputClass =
    'border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 text-sm ' +
    'bg-white dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 ' +
    'focus:outline-none focus:ring-2 focus:ring-blue-500'
  const buttonClass =
    'border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 dark:text-gray-200 ' +
    'rounded-lg px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40'

  const showChart = tags.length > 0 && trend && trend.series.length > 0

  return (
    <main className="py-6 flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Trend</h1>

      <form onSubmit={addTags} className="flex flex-wrap gap-2">
        <input
          type="text"
          autoFocus={tags.length === 0}
          value={tagInput}
          onChange={e => setTagInput(e.target.value)}
          placeholder="Add Aspen tags, e.g. FT21001, TT21002"
          className={`flex-1 min-w-48 ${inputClass}`}
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
        >
          Add
        </button>
      </form>

      {tags.length > 0 && (
        <ul className="flex flex-wrap gap-2">
          {tags.map(tag => (
            <li
              key={tag}
              className="flex items-center gap-1 text-sm bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300
                         pl-3 pr-1 py-1 rounded-full"
            >
              {tag}
              <button
                onClick={() => setTags(tags.filter(t => t !== tag))}
                title={`Remove ${tag}`}
                aria-label={`Remove ${tag}`}
                className="p-0.5 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900"
              >
                <X className="w-3.5 h-3.5" aria-hidden="true" />
              </button>
            </li>
          ))}
          <li>
            <button onClick={() => setTags([])} className="text-sm text-gray-500 dark:text-gray-400 hover:underline px-2 py-1">
              Clear all
            </button>
          </li>
        </ul>
      )}

      <div className="flex flex-wrap items-center gap-2">
        <select value={range} onChange={e => update({ range: e.target.value })} className={inputClass}>
          {RANGES.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
        </select>

        {range === 'custom' && (
          <>
            <input type="datetime-local" value={start} onChange={e => update({ start: e.target.value })}
                   aria-label="Start" className={inputClass} />
            <span className="text-sm text-gray-500 dark:text-gray-400">to</span>
            <input type="datetime-local" value={end} onChange={e => update({ end: e.target.value })}
                   aria-label="End" className={inputClass} />
          </>
        )}

        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 px-2">
          <input type="checkbox" checked={stacked} onChange={e => update({ stacked: e.target.checked })} />
          Separate axis per tag
        </label>

        <button
          onClick={() => setRefreshCount(n => n + 1)}
          disabled={!query || loading}
          title="Refresh"
          aria-label="Refresh"
          className={`${buttonClass} ml-auto`}
        >
          <RefreshCw className={`w-4 h-5 ${loading ? 'animate-spin' : ''}`} aria-hidden="true" />
        </button>
      </div>

      {error && <p className="text-red-500 text-sm">Trend failed: {error}</p>}

      {tags.length === 0 && (
        <p className="text-gray-400 dark:text-gray-500 text-sm">
          Add tags above, or use the trend button on Aspen AnalogDef and DiscreteDef search results.
        </p>
      )}

      {tags.length > 0 && trend && !error && (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {trend.start.replace('T', ' ')} to {trend.end.replace('T', ' ')}, one point every {trend.period_seconds}s
          {trend.missing.length > 0 && (
            <span className="text-amber-600 dark:text-amber-400">
              {' '}· No history for {trend.missing.join(', ')}
            </span>
          )}
        </p>
      )}

      {/* Kept mounted (just hidden) so Plotly can reuse the chart between fetches */}
      <div
        hidden={!showChart}
        className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-2"
      >
        <div ref={plotRef} className="w-full" />
      </div>
    </main>
  )
}

export default Trend
