import { useEffect, useState } from 'react'
import { STALE_DAYS, daysSince, getDatasets } from '../api'

// "Data loaded 2026-08-19 11:06 (26 days ago)" for one dataset from /api/datasets.
//
// Props:
//   dataset - key in /api/datasets, e.g. 'deltav_io'
function DataAge({ dataset }) {
  const [info, setInfo] = useState(null)

  useEffect(() => {
    let cancelled = false
    getDatasets()
      .then(all => {
        const entry = all[dataset]
        if (cancelled || !entry) return
        // Worked out once on load rather than on every render
        const days = entry.uploaded ? daysSince(entry.uploaded) : null
        setInfo({ ...entry, days })
      })
      .catch(() => {})  // data age is a nice-to-have; the search still works without it
    return () => { cancelled = true }
  }, [dataset])

  if (!info) return null

  if (!info.loaded) {
    return <p className="text-sm text-amber-700 dark:text-amber-400">No data loaded yet</p>
  }
  if (!info.uploaded) return null

  const { days } = info
  const stale = days > STALE_DAYS
  const ago = days <= 0 ? 'today' : `${days} day${days === 1 ? '' : 's'} ago`

  return (
    <p
      title={`${info.rows.toLocaleString()} rows`}
      className={`text-sm ${stale ? 'text-amber-700 dark:text-amber-400' : 'text-gray-500 dark:text-gray-400'}`}
    >
      Data loaded {info.uploaded.slice(0, 16)} ({ago}){stale && ', may be out of date'}
    </p>
  )
}

export default DataAge
