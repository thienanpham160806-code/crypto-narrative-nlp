import { useEffect, useMemo, useRef, useState } from 'react'
import { useT } from '../i18n.js'

const M = { top: 16, right: 56, bottom: 28, left: 48 }

function useWidth() {
  const ref = useRef(null)
  const [w, setW] = useState(600)
  useEffect(() => {
    const ro = new ResizeObserver(([e]) => setW(Math.max(280, e.contentRect.width)))
    ro.observe(ref.current)
    return () => ro.disconnect()
  }, [])
  return [ref, w]
}

function ticks(lo, hi, n = 4) {
  if (!(hi > lo)) return [lo]
  const step0 = (hi - lo) / n
  const mag = 10 ** Math.floor(Math.log10(step0))
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= step0)
  const out = []
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-12; v += step) out.push(+v.toFixed(10))
  return out
}

function dateTicks(t0, t1, w) {
  const span = (t1 - t0) / 864e5
  const n = Math.max(2, Math.floor(w / 110))
  const monthsStep = Math.max(1, Math.ceil(span / 30 / n))
  const out = []
  if (span <= 45) {
    const step = Math.max(1, Math.ceil(span / n))
    for (let d = new Date(t0); d <= t1; d = new Date(d.getTime() + step * 864e5)) out.push(d)
    return out
  }
  const d = new Date(Date.UTC(t0.getUTCFullYear(), t0.getUTCMonth() + 1, 1))
  for (; d <= t1; d.setUTCMonth(d.getUTCMonth() + monthsStep)) out.push(new Date(d))
  return out
}

/**
 * rows: [{t: Date, ...}] · series: [{key, label, color, kind: 'line'|'area'}] · stacked: cộng dồn các area
 * band: {lo, hi, color} dải bất định · splits: {valid, test} Date · log: thang log
 */
export default function TimeChart({ rows, series, stacked = false, height = 240, yFormat, splits, log = false, band, onPick }) {
  const { t, lang } = useT()
  const [ref, w] = useWidth()
  const [hover, setHover] = useState(null)
  const iw = w - M.left - M.right, ih = height - M.top - M.bottom

  const geo = useMemo(() => {
    if (!rows.length || !series.length) return null
    const t0 = rows[0].t, t1 = rows[rows.length - 1].t
    const span = Math.max(1, t1 - t0)
    const x = (d) => M.left + ((d - t0) / span) * iw
    const vals = []
    const stacks = []
    if (stacked) {
      const acc = new Array(rows.length).fill(0)
      for (const s of series) {
        const lo = acc.slice()
        rows.forEach((r, i) => { acc[i] += r[s.key] ?? 0 })
        stacks.push({ s, lo, hi: acc.slice() })
      }
      vals.push(0, ...stacks.at(-1).hi)
    } else {
      for (const s of series) for (const r of rows) if (r[s.key] != null) vals.push(r[s.key])
      if (band) for (const r of rows) { if (r[band.lo] != null) vals.push(r[band.lo]); if (r[band.hi] != null) vals.push(r[band.hi]) }
    }
    let lo = Math.min(...vals), hi = Math.max(...vals)
    if (!vals.length) { lo = 0; hi = 1 }
    if (!log && lo > 0 && !stacked && lo / hi < 0.5) lo = Math.min(lo, 0)
    if (lo === hi) { lo -= 1; hi += 1 }
    const f = log ? Math.log10 : (v) => v
    const L = f(lo), H = f(hi)
    const y = (v) => M.top + ih - ((f(v) - L) / (H - L)) * ih
    const yt = log ? ticks(Math.floor(L), Math.ceil(H), 3).map((p) => 10 ** p).filter((v) => v >= lo && v <= hi) : ticks(lo, hi)
    return { t0, t1, x, y, yt, stacks, lo }
  }, [rows, series, stacked, iw, ih, log, band])

  if (!rows.length || !geo) return <div ref={ref} className="empty">{t.noData}</div>
  const { x, y, yt, stacks } = geo

  const path = (key) => {
    let d = '', pen = false
    rows.forEach((r) => {
      const v = r[key]
      if (v == null || Number.isNaN(v)) { pen = false; return }
      d += `${pen ? 'L' : 'M'}${x(r.t).toFixed(1)},${y(v).toFixed(1)}`
      pen = true
    })
    return d
  }
  const area = (lo, hi) => {
    const top = rows.map((r, i) => `${x(r.t).toFixed(1)},${y(hi[i]).toFixed(1)}`).join('L')
    const bot = rows.map((r, i) => `${x(r.t).toFixed(1)},${y(lo[i]).toFixed(1)}`).reverse().join('L')
    return `M${top}L${bot}Z`
  }
  const bandPath = band && (() => {
    const pts = rows.filter((r) => r[band.lo] != null && r[band.hi] != null)
    if (!pts.length) return null
    return `M${pts.map((r) => `${x(r.t).toFixed(1)},${y(r[band.hi]).toFixed(1)}`).join('L')}L${pts.map((r) => `${x(r.t).toFixed(1)},${y(r[band.lo]).toFixed(1)}`).reverse().join('L')}Z`
  })()

  const pick = (px) => {
    let best = 0, bd = Infinity
    rows.forEach((r, i) => { const d = Math.abs(x(r.t) - px); if (d < bd) { bd = d; best = i } })
    return best
  }
  const move = (e) => {
    const box = e.currentTarget.getBoundingClientRect()
    setHover(pick(((e.clientX - box.left) / box.width) * w))
  }
  const key = (e) => {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return
    e.preventDefault()
    setHover((h) => Math.min(rows.length - 1, Math.max(0, (h ?? rows.length - 1) + (e.key === 'ArrowRight' ? 1 : -1))))
  }
  const clampSplit = (d) => (d && d > geo.t0 && d < geo.t1 ? x(d) : d && d <= geo.t0 ? M.left : null)
  const xv = clampSplit(splits?.valid), xt = clampSplit(splits?.test)
  const right = M.left + iw
  const fmtDate = (d) => d.toLocaleDateString(lang === 'vi' ? 'vi-VN' : 'en-GB', { timeZone: 'UTC', day: '2-digit', month: 'short', year: 'numeric' })
  const fmtTick = (d) => d.toLocaleDateString(lang === 'vi' ? 'vi-VN' : 'en-GB', { timeZone: 'UTC', month: 'short', year: (geo.t1 - geo.t0) > 300 * 864e5 ? '2-digit' : undefined, day: (geo.t1 - geo.t0) <= 45 * 864e5 ? '2-digit' : undefined })
  const h = hover != null ? rows[hover] : null
  const last = rows[rows.length - 1]

  return (
    <div className="chart" ref={ref}>
      <svg viewBox={`0 0 ${w} ${height}`} height={height} role="img" tabIndex={0}
        aria-label={series.map((s) => s.label).join(', ')}
        onPointerMove={move} onPointerLeave={() => setHover(null)} onKeyDown={key} onBlur={() => setHover(null)}
        onClick={() => onPick && h && onPick(h)}>
        {xv != null && <rect className="band-valid" x={xv} y={M.top} width={(xt ?? right) - xv} height={ih} />}
        {xt != null && <rect className="band-test" x={xt} y={M.top} width={right - xt} height={ih} />}
        {xv != null && (xt ?? right) - xv > 40 && <text className="band-label" x={xv + 4} y={M.top + 12}>{'Valid'}</text>}
        {xt != null && right - xt > 40 && <text className="band-label" x={xt + 4} y={M.top + 12}>{'Test'}</text>}
        <g className="grid">{yt.map((v) => <line key={v} x1={M.left} x2={right} y1={y(v)} y2={y(v)} />)}</g>
        <g className="axis">
          {yt.map((v) => <text key={v} x={M.left - 8} y={y(v) + 4} textAnchor="end">{yFormat ? yFormat(v) : v}</text>)}
          {dateTicks(geo.t0, geo.t1, iw).map((d) => <text key={+d} x={x(d)} y={height - 8} textAnchor="middle">{fmtTick(d)}</text>)}
        </g>
        <line className="baseline" x1={M.left} x2={right} y1={M.top + ih} y2={M.top + ih} />
        {bandPath && <path d={bandPath} fill={band.color} opacity="0.18" />}
        {stacks.map(({ s, lo, hi }) => (
          <path key={s.key} d={area(lo, hi)} fill={s.color} stroke="var(--surface)" strokeWidth={rows.length > iw / 4 ? 0 : 1} />
        ))}
        {!stacked && series.map((s) => (
          <path key={s.key} d={path(s.key)} fill="none" stroke={s.color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
        ))}
        {!stacked && series.length <= 4 && series.map((s) => last[s.key] != null && (
          <g key={s.key}>
            <circle cx={x(last.t)} cy={y(last[s.key])} r="4" fill={s.color} stroke="var(--surface)" strokeWidth="2" />
            <text className="axis" x={x(last.t) + 8} y={y(last[s.key]) + 4} fill="var(--ink-2)" fontSize="11">
              {yFormat ? yFormat(last[s.key]) : last[s.key]}
            </text>
          </g>
        ))}
        {h && <line className="cross" x1={x(h.t)} x2={x(h.t)} y1={M.top} y2={M.top + ih} />}
        {h && !stacked && series.map((s) => h[s.key] != null && (
          <circle key={s.key} cx={x(h.t)} cy={y(h[s.key])} r="4" fill={s.color} stroke="var(--surface)" strokeWidth="2" />
        ))}
      </svg>
      {h && (
        <div className="tip" style={{ left: Math.min(x(h.t) / w * 100, 70) + '%', top: 8 }}>
          <div className="when">{fmtDate(h.t)} UTC</div>
          {[...series].reverse().map((s) => (
            <div className="row" key={s.key}>
              <span><i className="key-line" style={{ background: s.color }} />{s.label}</span>
              <strong>{h[s.key] == null ? '–' : yFormat ? yFormat(h[s.key]) : h[s.key]}</strong>
            </div>
          ))}
          {band && h[band.lo] != null && (
            <div className="row"><span>{band.label}</span><strong>{yFormat(h[band.lo])} – {yFormat(h[band.hi])}</strong></div>
          )}
        </div>
      )}
    </div>
  )
}
