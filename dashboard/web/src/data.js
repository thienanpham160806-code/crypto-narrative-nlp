import { useEffect, useState } from 'react'

const cache = new Map()

export function load(name) {
  if (!cache.has(name)) {
    cache.set(name, fetch(`${import.meta.env.BASE_URL}data/${name}.json`).then((r) => {
      if (!r.ok) throw new Error(`${name}.json: HTTP ${r.status}`)
      return r.json()
    }))
  }
  return cache.get(name)
}

export function useData(name) {
  const [state, set] = useState({ data: null, error: null })
  useEffect(() => {
    let live = true
    load(name).then((data) => live && set({ data, error: null }), (error) => live && set({ data: null, error }))
    return () => { live = false }
  }, [name])
  return state
}

export const day = (s) => new Date(s.slice(0, 10) + 'T00:00:00Z')
export const iso = (d) => d.toISOString().slice(0, 10)

export function rolling(rows, key, n = 7) {
  const out = new Array(rows.length).fill(null)
  for (let i = 0; i < rows.length; i++) {
    let s = 0, k = 0
    for (let j = Math.max(0, i - n + 1); j <= i; j++) {
      const v = rows[j][key]
      if (v != null && !Number.isNaN(v)) { s += v; k++ }
    }
    out[i] = k ? s / k : null
  }
  return out
}

export function inRange(rows, range, end) {
  if (range === 'all' || !rows.length) return rows
  const last = end ?? rows[rows.length - 1].t
  const from = new Date(last.getTime() - (range - 1) * 864e5)
  return rows.filter((r) => r.t >= from && r.t <= last)
}
