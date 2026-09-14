import { useEffect, useState } from 'react'
import { CircleCheck, CircleX, LoaderCircle, RefreshCw, TriangleAlert } from 'lucide-react'
import { STALE_DAYS, daysSince } from '../api'

// Friendly names and the command that reloads each dataset from /api/health
const DATASETS = {
  intellution: { label: 'Intellution tags', command: 'init-intellution' },
  deltav: { label: 'DeltaV modules', command: 'init-deltav' },
  deltav_io: { label: 'DeltaV IO channels', command: 'init-deltav-io' },
  truthtables: { label: 'GCC truthtables', command: 'init-ttparser' },
  team: { label: 'Controls team', command: 'init-team' },
}

// /api/health answers 503 with a JSON body when something is down, so read the
// body whatever the status code rather than treating 503 as a failed request
async function fetchHealth(url) {
  const res = await fetch(url)
  const data = await res.json().catch(() => null)
  if (!data) throw new Error(`HTTP ${res.status}`)
  return { ...data, checkedAt: new Date().toLocaleTimeString() }
}

const TONES = {
  ok: { Icon: CircleCheck, className: 'text-green-600 dark:text-green-400' },
  warn: { Icon: TriangleAlert, className: 'text-amber-600 dark:text-amber-400' },
  error: { Icon: CircleX, className: 'text-red-600 dark:text-red-400' },
  checking: { Icon: LoaderCircle, className: 'text-gray-400 dark:text-gray-500 animate-spin' },
}

function StatusIcon({ tone }) {
  const { Icon, className } = TONES[tone]
  return <Icon className={`w-5 h-5 shrink-0 ${className}`} aria-hidden="true" />
}

// One headline check: Database, Aspen, ...
function CheckCard({ title, tone, detail }) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-5 flex items-start gap-3">
      <StatusIcon tone={tone} />
      <div className="min-w-0">
        <h2 className="font-semibold text-gray-800 dark:text-gray-100">{title}</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 break-words">{detail}</p>
      </div>
    </div>
  )
}

function datasetState(info) {
  if (!info.loaded) return { tone: 'error', text: 'Not loaded' }
  if (!info.uploaded) return { tone: 'ok', text: 'Loaded' }
  const days = daysSince(info.uploaded)
  const ago = days <= 0 ? 'today' : `${days} day${days === 1 ? '' : 's'} ago`
  return days > STALE_DAYS
    ? { tone: 'warn', text: `${ago}, may be out of date` }
    : { tone: 'ok', text: ago }
}

// Props:
//   user - signed-in account name, or null
function Status({ user }) {
  // Bumped by the refresh button to run every check again
  const [refreshCount, setRefreshCount] = useState(0)
  // Each finished check, tagged with the refresh it belongs to: { key, data, error }
  const [health, setHealth] = useState(null)
  const [aspen, setAspen] = useState(null)

  // The database check is quick; Aspen can take up to its connection timeout,
  // so it runs separately and doesn't hold up the rest of the page
  useEffect(() => {
    let cancelled = false
    const settle = setter => [
      data => { if (!cancelled) setter({ key: refreshCount, data, error: null }) },
      err => { if (!cancelled) setter({ key: refreshCount, data: null, error: err.message }) },
    ]
    fetchHealth('/api/health').then(...settle(setHealth))
    fetchHealth('/api/health?aspen=1').then(...settle(setAspen))
    return () => { cancelled = true }
  }, [refreshCount])

  const healthDone = health?.key === refreshCount
  const aspenDone = aspen?.key === refreshCount
  const body = health?.data

  let databaseCard
  if (!healthDone) databaseCard = { tone: 'checking', detail: 'Checking...' }
  else if (health.error) databaseCard = { tone: 'error', detail: `Couldn't reach the server: ${health.error}` }
  else if (body.database === 'ok') databaseCard = { tone: 'ok', detail: 'Connected' }
  else databaseCard = { tone: 'error', detail: body.error ?? 'Unreachable' }

  let aspenCard
  if (!aspenDone) aspenCard = { tone: 'checking', detail: 'Testing connection (can take a few seconds)...' }
  else if (aspen.error) aspenCard = { tone: 'error', detail: aspen.error }
  else if (aspen.data.aspen === 'ok') aspenCard = { tone: 'ok', detail: 'Connected' }
  else aspenCard = { tone: 'error', detail: aspen.data.aspen_error ?? aspen.data.error ?? 'Unable to connect; see the server log' }

  const signInCard = user
    ? { tone: 'ok', detail: user }
    : body?.error === 'Sign-in required'
      ? { tone: 'error', detail: 'Not signed in; check Windows Authentication in IIS' }
      : { tone: 'warn', detail: 'No sign-in (fine in development)' }

  const datasets = body?.datasets

  return (
    <main className="py-6 flex flex-col gap-6">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">System Status</h1>
        {healthDone && health.data && (
          <span className="text-sm text-gray-500 dark:text-gray-400">Checked at {health.data.checkedAt}</span>
        )}
        <button
          onClick={() => setRefreshCount(n => n + 1)}
          disabled={!healthDone || !aspenDone}
          title="Check again"
          aria-label="Check again"
          className="ml-auto border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 dark:text-gray-200
                     rounded-lg px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40"
        >
          <RefreshCw className={`w-4 h-5 ${!healthDone || !aspenDone ? 'animate-spin' : ''}`} aria-hidden="true" />
        </button>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CheckCard title="Database" {...databaseCard} />
        <CheckCard title="Aspen" {...aspenCard} />
        <CheckCard title="Signed in as" {...signInCard} />
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-200">Datasets</h2>
        {!datasets && healthDone && (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Dataset details aren't available: {health.error ?? body?.error ?? 'the database is unreachable'}.
          </p>
        )}
        {datasets && (
          <div className="overflow-x-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200">
                <tr>
                  <th className="px-4 py-2 font-semibold">Dataset</th>
                  <th className="px-4 py-2 font-semibold text-right">Rows</th>
                  <th className="px-4 py-2 font-semibold">Last loaded</th>
                  <th className="px-4 py-2 font-semibold">Status</th>
                  <th className="px-4 py-2 font-semibold">Reload with</th>
                </tr>
              </thead>
              <tbody className="text-gray-800 dark:text-gray-200">
                {Object.entries(datasets).map(([key, info]) => {
                  const { label, command } = DATASETS[key] ?? { label: key, command: null }
                  const state = datasetState(info)
                  return (
                    <tr key={key} className="border-t border-gray-100 dark:border-gray-800">
                      <td className="px-4 py-2 whitespace-nowrap">{label}</td>
                      <td className="px-4 py-2 text-right tabular-nums">{info.rows.toLocaleString()}</td>
                      <td className="px-4 py-2 whitespace-nowrap">{info.uploaded?.slice(0, 16) ?? '—'}</td>
                      <td className="px-4 py-2">
                        <span className="flex items-center gap-2 whitespace-nowrap">
                          <StatusIcon tone={state.tone} />
                          {state.text}
                        </span>
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap">
                        {command && <code className="text-xs text-gray-600 dark:text-gray-400">flask {command}</code>}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Data older than {STALE_DAYS} days is flagged. <code>flask init-all</code> reloads everything.
          Monitors can poll <code>/api/health</code>, which answers 503 when something is down.
        </p>
      </section>
    </main>
  )
}

export default Status
