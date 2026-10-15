// Small helpers for talking to the Flask API.

// The app is served under a sub-path (Vite's base, /acp/): '/api/team' -> '/acp/api/team'
export const BASE_PATH = import.meta.env.BASE_URL.replace(/\/$/, '')
export const withBase = path => BASE_PATH + path

// Fetch JSON, turning the API's { error } replies into thrown errors
export async function fetchJson(url, options) {
  const res = await fetch(withBase(url), options)
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new Error(data?.error ?? `HTTP ${res.status}`)
  return data
}

// Data older than this is flagged, since exports are loaded by hand
export const STALE_DAYS = 30

// Whole days since an API timestamp like "2026-08-19 11:06:05"
export function daysSince(timestamp) {
  return Math.floor((Date.now() - new Date(timestamp.replace(' ', 'T'))) / 86_400_000)
}

// Loaded once per browser session and shared by every page that shows data age
let datasetsPromise = null
export function getDatasets() {
  datasetsPromise ??= fetchJson('/api/datasets').catch(err => {
    datasetsPromise = null  // try again next time instead of caching the failure
    throw err
  })
  return datasetsPromise
}

// Split typed or pasted text like "FT21001, TT21002" into tags
export function splitTags(text) {
  return String(text ?? '').split(/[\s,]+/).map(t => t.trim()).filter(Boolean)
}

const LAST_TREND_KEY = 'trend.lastQuery'

// Remember the trend page's query so tags added from a search join the same trend
export function rememberTrendQuery(query) {
  try {
    sessionStorage.setItem(LAST_TREND_KEY, query)
  } catch {
    // Storage can be blocked; new tags then just start a fresh trend
  }
}

// URL for the trend page with `newTags` added to the last trend's tags and settings
export function trendUrl(newTags) {
  let params
  try {
    params = new URLSearchParams(sessionStorage.getItem(LAST_TREND_KEY) ?? '')
  } catch {
    params = new URLSearchParams()
  }
  const tags = splitTags(params.get('tags'))
  for (const tag of [newTags].flat().flatMap(splitTags)) {
    if (!tags.includes(tag)) tags.push(tag)
  }
  params.set('tags', tags.join(','))
  return `/trend?${params}`
}
