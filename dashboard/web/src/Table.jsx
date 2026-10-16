import { useMemo, useState } from 'react'
import { useT } from './i18n.js'

/** cols: [{key, label, num?, format?}] · bảng sắp xếp được, thay thế cho mọi biểu đồ. */
export default function Table({ rows, cols, max = 2000 }) {
  const { t } = useT()
  const [sort, setSort] = useState(null)
  const sorted = useMemo(() => {
    if (!sort) return rows
    const { key, dir } = sort
    return [...rows].sort((a, b) => {
      const x = a[key], y = b[key]
      if (x == null) return 1
      if (y == null) return -1
      return (x > y ? 1 : x < y ? -1 : 0) * dir
    })
  }, [rows, sort])
  if (!rows.length) return <div className="empty">{t.noData}</div>
  const toggle = (key) => setSort((s) => ({ key, dir: s?.key === key ? -s.dir : -1 }))
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>{cols.map((c) => (
            <th key={c.key} className={c.num ? 'n' : ''} aria-sort={sort?.key === c.key ? (sort.dir > 0 ? 'ascending' : 'descending') : 'none'}>
              <button onClick={() => toggle(c.key)} title={`${t.sortBy} ${c.label}`}>{c.label}{sort?.key === c.key ? (sort.dir > 0 ? ' ↑' : ' ↓') : ''}</button>
            </th>
          ))}</tr>
        </thead>
        <tbody>
          {sorted.slice(0, max).map((r, i) => (
            <tr key={i}>{cols.map((c) => (
              <td key={c.key} className={c.num ? 'n' : ''}>{c.format ? c.format(r[c.key], r) : r[c.key] ?? '–'}</td>
            ))}</tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
