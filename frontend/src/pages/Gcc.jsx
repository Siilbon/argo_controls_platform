import { useState } from 'react'
import DataTable from '../components/DataTable'
import { fetchJson } from '../api'

const EOS_FIELDS = ['eos_type', 'eos_mod1', 'eos_mod2', 'eos_mod3', 'eos_mod4',
                    'eos_mod5', 'eos_mod6', 'eos_mod7', 'eos_mod8']

const inputClass =
  'w-full border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 text-sm ' +
  'bg-white dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 ' +
  'focus:outline-none focus:ring-2 focus:ring-blue-500'
const labelClass = 'text-sm text-gray-600 dark:text-gray-400'
const submitClass =
  'bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors disabled:opacity-50'
const cardClass =
  'bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 flex flex-col gap-4'

// Props:
//   eosType - EOS type to start the translator with (from the home page card)
function EosTranslator({ eosType }) {
  const [values, setValues] = useState(() => ({
    ...Object.fromEntries(EOS_FIELDS.map(f => [f, ''])),
    eos_type: eosType ?? '',
  }))
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      // Blank modifiers are sent as 0, matching the old form's defaults
      const body = Object.fromEntries(EOS_FIELDS.map(f => [f, Number(values[f] || 0)]))
      setResult(await fetchJson('/api/gcc/eos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className={cardClass}>
      <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">End of Step Translator</h2>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <label className="flex flex-col gap-1">
          <span className={labelClass}>EOS Type</span>
          <input
            type="number"
            required
            autoFocus
            value={values.eos_type}
            onChange={e => setValues({ ...values, eos_type: e.target.value })}
            className={inputClass}
          />
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {EOS_FIELDS.slice(1).map((field, i) => (
            <label key={field} className="flex flex-col gap-1">
              <span className={labelClass}>Mod {i + 1}</span>
              <input
                type="number"
                placeholder="0"
                value={values[field]}
                onChange={e => setValues({ ...values, [field]: e.target.value })}
                className={inputClass}
              />
            </label>
          ))}
        </div>
        <div>
          <button type="submit" disabled={loading} className={submitClass}>
            English, please...
          </button>
        </div>
      </form>

      {error && <p className="text-red-500 text-sm">Translation failed: {error}</p>}

      {result && !error && (
        result.step_not_found ? (
          <p className="text-sm text-amber-700 dark:text-amber-400">
            {result.message} isn't in this tool yet. It may still be valid; ask Karl if you'd like it added.
          </p>
        ) : (
          <p className="text-gray-800 dark:text-gray-100">{result.message}</p>
        )
      )}
    </section>
  )
}

function TruthtableLookup() {
  const [name, setName] = useState('')
  const [seq, setSeq] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      setResult(await fetchJson(
        `/api/ttparser/${encodeURIComponent(name.trim())}/${encodeURIComponent(seq)}`))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className={cardClass}>
      <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Truthtable</h2>

      <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1 flex-1 min-w-40">
          <span className={labelClass}>Truthtable unit name</span>
          <input
            type="text"
            required
            placeholder="e.g. 41IX1X"
            value={name}
            onChange={e => setName(e.target.value)}
            className={inputClass}
          />
        </label>
        <label className="flex flex-col gap-1 w-32">
          <span className={labelClass}>Sequence</span>
          <input
            type="number"
            required
            min="0"
            value={seq}
            onChange={e => setSeq(e.target.value)}
            className={inputClass}
          />
        </label>
        <button type="submit" disabled={loading} className={submitClass}>
          Read Truthtable
        </button>
      </form>

      {error && <p className="text-red-500 text-sm">Lookup failed: {error}</p>}
      {loading && <p className="text-gray-400 dark:text-gray-500 text-sm">Loading...</p>}

      {result && (
        <DataTable
          data={result.data}
          storageKey="gcc_truthtable.columnVisibility"
          exportName={`truthtable_${result.ttname}_seq${result.seqnum}`}
        />
      )}
    </section>
  )
}

// Props:
//   eosType - optional EOS type to prefill, e.g. from the home page card
function Gcc({ eosType }) {
  return (
    // Narrower than the data pages: these are short forms
    <main className="max-w-4xl py-6 flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">GCC Tools</h1>
      <EosTranslator eosType={eosType} />
      <TruthtableLookup />
    </main>
  )
}

export default Gcc
