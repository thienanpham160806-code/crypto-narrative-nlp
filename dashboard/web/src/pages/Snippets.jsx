import { useMemo, useState } from 'react'
import { useT, fmt, NARR_LABEL } from '../i18n.js'
import { useData, day } from '../data.js'
import Exhibit from '../Exhibit.jsx'
import { COLORS } from './Overview.jsx'

/** Tin đại diện trong khoảng thời gian đang lọc; lọc theo narrative. */
export default function Snippets({ no, narrative: fixed, limit = 12 }) {
  const { t, lang, meta, range, end } = useT()
  const { data } = useData('snippets')
  const [narr, setNarr] = useState(fixed ?? 'all')
  const items = useMemo(() => {
    if (!data || !end) return []
    const from = range === 'all' ? null : new Date(end.getTime() - (range - 1) * 864e5)
    return data.filter((s) => {
      const d = day(s.public_ts_utc)
      return d <= end && (!from || d >= from) && (narr === 'all' || s.narrative === narr)
    }).slice(-limit).reverse()
  }, [data, range, end, narr, limit])
  if (!meta) return null
  const color = (k) => COLORS[meta.narratives.indexOf(k)] ?? 'var(--muted)'
  const when = (s) => s.public_ts_utc.replace('T', ' ').slice(0, 16)
  return (
    <Exhibit no={no} title={t.ex.snippets[0]} sub={t.ex.snippets[1]} span2 source={t.source.gdelt}
      legend={!fixed && (
        <div className="chips" role="group" aria-label="Narrative" style={{ marginBottom: 8, flexWrap: 'wrap' }}>
          {['all', ...meta.narratives].map((k) => (
            <button key={k} aria-pressed={narr === k} onClick={() => setNarr(k)}>{k === 'all' ? t.all : NARR_LABEL[k]}</button>
          ))}
        </div>
      )}
      chart={items.length ? (
        <ul className="snips">
          {items.map((s) => (
            <li key={s.doc_id}>
              <time className="num" dateTime={s.public_ts_utc}>{when(s)} UTC · {s.source}</time>
              <a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a>
              <span className="tag"><i className="key-rect" style={{ background: color(s.narrative) }} />{NARR_LABEL[s.narrative] ?? s.narrative}</span>
              {s.finbert_sentiment != null && (
                <span className={`score num ${s.finbert_sentiment < 0 ? 'neg' : 'pos'}`}>FinBERT {fmt(lang, s.finbert_sentiment, 2, { signed: true })}</span>
              )}
              {s.asset_tags?.length > 0 && <span className="tag">{s.asset_tags.join(' · ')}</span>}
            </li>
          ))}
        </ul>
      ) : <div className="empty">{t.noData}</div>} />
  )
}
