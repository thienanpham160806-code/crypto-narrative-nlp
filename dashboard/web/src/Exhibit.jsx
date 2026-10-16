import { useState } from 'react'
import { useT } from './i18n.js'

/** Exhibit đánh số kiểu báo cáo chính sách: tiêu đề, phụ đề, Hình/Bảng, nhận định, nguồn. */
export default function Exhibit({ no, title, sub, judgement, source, chart, table, span2 = false, legend }) {
  const { t } = useT()
  const [view, setView] = useState('chart')
  return (
    <section className={`exhibit${span2 ? ' span2' : ''}`} aria-labelledby={`ex-${no}`}>
      <div className="ex-head">
        <h2 id={`ex-${no}`}><span className="no">Exhibit {no}</span>{title}</h2>
        {table && chart && (
          <div className="view-toggle" role="group" aria-label={`${t.view.chart} / ${t.view.table}`}>
            <button aria-pressed={view === 'chart'} onClick={() => setView('chart')}>{t.view.chart}</button>
            <button aria-pressed={view === 'table'} onClick={() => setView('table')}>{t.view.table}</button>
          </div>
        )}
      </div>
      {sub && <p className="ex-sub">{sub}</p>}
      {view === 'chart' && legend}
      {view === 'chart' ? chart ?? table : table}
      {judgement && <p className="ex-judgement">{judgement}</p>}
      {source && <p className="ex-source">{source}</p>}
    </section>
  )
}

export function Legend({ items, hidden, onToggle, kind = 'rect' }) {
  return (
    <div className="legend">
      {items.map((s) => (
        <button key={s.key} aria-pressed={!hidden?.has(s.key)} onClick={() => onToggle?.(s.key)} disabled={!onToggle}>
          <i className={kind === 'line' ? 'key-line' : 'key-rect'} style={{ background: s.color }} />{s.label}
        </button>
      ))}
    </div>
  )
}
