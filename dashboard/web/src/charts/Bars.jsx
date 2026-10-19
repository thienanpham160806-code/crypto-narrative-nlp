import { useState } from 'react'
import { useT } from '../i18n.js'

/** Thanh ngang, một chuỗi: rows [{label, value, note?}], giá trị ở đầu thanh. */
export default function Bars({ rows, format = (v) => v, color = 'var(--s1)' }) {
  const { t } = useT()
  const [hover, setHover] = useState(null)
  const ok = rows.filter((r) => r.value != null && !Number.isNaN(r.value))
  if (!ok.length) return <div className="empty">{t.noData}</div>
  const max = Math.max(...ok.map((r) => r.value)) || 1
  const rowH = 32, labelW = 150, w = 560, plot = w - labelW - 70
  return (
    <div className="chart">
      <svg viewBox={`0 0 ${w} ${rows.length * rowH + 8}`} role="img" aria-label={rows.map((r) => r.label).join(', ')}>
        {rows.map((r, i) => {
          const len = r.value == null ? 0 : Math.max(2, (r.value / max) * plot)
          const yy = i * rowH + 8
          return (
            <g key={r.label} onPointerEnter={() => setHover(i)} onPointerLeave={() => setHover(null)} tabIndex={0}
              onFocus={() => setHover(i)} onBlur={() => setHover(null)}>
              <rect x="0" y={yy - 4} width={w} height={rowH} fill="transparent" />
              <text x={labelW - 10} y={yy + 13} textAnchor="end" fontSize="12" fill="var(--ink-2)">{r.label}</text>
              <path d={`M${labelW},${yy + 4}h${Math.max(0, len - 4)}a4,4 0 0 1 4,4v8a4,4 0 0 1 -4,4h${-Math.max(0, len - 4)}z`}
                fill={color} opacity={hover == null || hover === i ? 1 : 0.55} />
              <text x={labelW + len + 6} y={yy + 13} fontSize="12" fill="var(--ink)" className="num">
                {r.value == null ? '–' : format(r.value)}
              </text>
            </g>
          )
        })}
      </svg>
      {hover != null && rows[hover].note && <p className="note">{rows[hover].label}: {rows[hover].note}</p>}
    </div>
  )
}
