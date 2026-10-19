import { useEffect, useState } from 'react'
import { useT, fmt, NARR_LABEL } from '../i18n.js'
import { load } from '../data.js'
import { COLORS } from './Overview.jsx'

/** Tin RSS mới nhất: local gọi /api/live (chấm trực tiếp); Vercel đọc bản chụp data/live.json. */
export default function Live() {
  const { t, lang, meta } = useT()
  const [state, set] = useState({ items: null, updated: null, error: null })
  useEffect(() => {
    let live = true
    const take = (d) => live && set({ items: d.items ?? [], updated: d.updated_utc, error: null })
    fetch('/api/live').then((r) => (r.ok ? r.json() : Promise.reject(r))).then(take)
      .catch(() => load('live').then(take, (error) => live && set({ items: [], updated: null, error })))
    return () => { live = false }
  }, [])
  const color = (k) => COLORS[meta?.narratives.indexOf(k)] ?? 'var(--muted)'
  return (
    <div className="exhibits full">
      <section className="exhibit span2" aria-labelledby="live-h">
        <div className="ex-head"><h2 id="live-h">{t.live.title}</h2></div>
        <p className="ex-sub">{t.live.note}{state.updated && ` ${t.live.updated}: ${state.updated.replace('T', ' ').slice(0, 16)} UTC.`}</p>
        {state.items == null ? <div className="empty">…</div> : state.items.length === 0 ? <div className="empty">{t.noData}</div> : (
          <ul className="snips">
            {state.items.map((s) => (
              <li key={s.url}>
                <time className="num" dateTime={s.public_ts_utc}>{s.public_ts_utc.replace('T', ' ').slice(0, 16)} UTC · {s.source}</time>
                <a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a>
                <span className="tag"><i className="key-rect" style={{ background: color(s.narrative) }} />{NARR_LABEL[s.narrative] ?? s.narrative}</span>
                {s.finbert_sentiment != null && <span className={`score num ${s.finbert_sentiment < 0 ? 'neg' : 'pos'}`}>FinBERT {fmt(lang, s.finbert_sentiment, 2, { signed: true })}</span>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
