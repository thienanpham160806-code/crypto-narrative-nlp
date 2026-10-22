import { useEffect, useRef, useState } from 'react'
import { useT, fmt, NARR_LABEL } from '../i18n.js'
import { load } from '../data.js'
import { COLORS } from './Overview.jsx'

const REFRESH_S = 30
const PAIRS = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']
const WS = 'wss://data-stream.binance.vision/stream?streams=' + PAIRS.map((p) => `${p.toLowerCase()}usdt@miniTicker`).join('/')

/** Giá Binance theo thời gian thực (miniTicker 24h qua WebSocket dữ liệu thị trường công khai). */
function usePrices() {
  const [px, set] = useState({})
  useEffect(() => {
    let ws, retry, stop = false
    const open = () => {
      ws = new WebSocket(WS)
      ws.onmessage = (e) => {
        const d = JSON.parse(e.data).data
        const sym = d.s.replace('USDT', '')
        set((p) => ({ ...p, [sym]: { price: +d.c, chg: +d.c / +d.o - 1, dir: p[sym] ? Math.sign(+d.c - p[sym].price) : 0, at: Date.now() } }))
      }
      ws.onclose = () => { if (!stop) retry = setTimeout(open, 3000) }
    }
    open()
    return () => { stop = true; clearTimeout(retry); ws?.close() }
  }, [])
  return px
}

/** Tin mới: /api/live mỗi 30 giây khi tab đang mở; lỗi thì đọc bản chụp data/live.json. Đánh dấu tin mới xuất hiện. */
function useNews() {
  const [st, set] = useState({ items: null, updated: null, scoring: null, fetchedAt: null })
  const seen = useRef(new Set())
  useEffect(() => {
    let alive = true
    const take = (d) => {
      if (!alive) return
      const first = seen.current.size === 0
      const items = (d.items ?? []).map((s) => ({ ...s, fresh: !first && !seen.current.has(s.url) }))
      items.forEach((s) => seen.current.add(s.url))
      set({ items, updated: d.updated_utc, scoring: d.scoring ?? 'finbert', fetchedAt: Date.now() })
    }
    const pull = () => fetch('/api/live', { cache: 'no-store' }).then((r) => (r.ok ? r.json() : Promise.reject(r))).then(take)
      .catch(() => load('live').then(take, () => alive && set((s) => ({ ...s, items: s.items ?? [] }))))
    pull()
    const id = setInterval(() => document.visibilityState === 'visible' && pull(), REFRESH_S * 1000)
    return () => { alive = false; clearInterval(id) }
  }, [])
  return st
}

function useNow(ms = 1000) {
  const [now, set] = useState(Date.now())
  useEffect(() => { const id = setInterval(() => set(Date.now()), ms); return () => clearInterval(id) }, [ms])
  return now
}

const ago = (lang, ts, now) => {
  const s = Math.max(0, Math.round((now - Date.parse(ts)) / 1000))
  const [v, u] = s < 60 ? [s, 's'] : s < 3600 ? [Math.floor(s / 60), 'm'] : s < 86400 ? [Math.floor(s / 3600), 'h'] : [Math.floor(s / 86400), 'd']
  const unit = lang === 'vi' ? { s: 'giây', m: 'phút', h: 'giờ', d: 'ngày' }[u] : { s: 's', m: 'min', h: 'h', d: 'd' }[u]
  return lang === 'vi' ? `${v} ${unit} trước` : `${v}${unit === 'min' ? ' min' : unit} ago`
}

export default function Live() {
  const { t, lang, meta } = useT()
  const px = usePrices()
  const news = useNews()
  const now = useNow()
  const color = (k) => COLORS[meta?.narratives.indexOf(k)] ?? 'var(--muted)'
  const next = news.fetchedAt ? Math.max(0, REFRESH_S - Math.floor((now - news.fetchedAt) / 1000)) : null
  return (
    <div className="exhibits full">
      <section className="exhibit span2" aria-labelledby="px-h">
        <div className="ex-head"><h2 id="px-h">{t.live.prices}</h2><span className="live-dot" aria-hidden="true" /></div>
        <div className="ticker" role="list">
          {PAIRS.map((p) => {
            const q = px[p]
            return (
              <div key={p} role="listitem" className="tick">
                <span className="sym">{p}</span>
                <span className={`num px ${q?.dir > 0 ? 'up' : q?.dir < 0 ? 'down' : ''}`} key={q?.at}>{q ? fmt(lang, q.price, q.price < 10 ? 4 : 2) : '…'}</span>
                <span className={`num chg ${q?.chg < 0 ? 'neg' : 'pos'}`}>{q ? fmt(lang, q.chg, 2, { signed: true, pct: true }) : ''}</span>
              </div>
            )
          })}
        </div>
        <p className="ex-sub">{t.live.priceNote}</p>
      </section>

      <section className="exhibit span2" aria-labelledby="live-h">
        <div className="ex-head"><h2 id="live-h">{t.live.title}</h2></div>
        <p className="ex-sub">
          {news.scoring === 'keyword' ? t.live.noteKeyword : t.live.note}
          {news.updated && ` ${t.live.updated}: ${news.updated.replace('T', ' ').slice(0, 19)} UTC`}
          {next != null && ` · ${t.live.refresh} ${next}s`}
        </p>
        {news.items == null ? <div className="empty">…</div> : news.items.length === 0 ? <div className="empty">{t.noData}</div> : (
          <ul className="snips" aria-live="polite">
            {news.items.map((s) => (
              <li key={s.url} className={s.fresh ? 'fresh' : undefined}>
                <time className="num" dateTime={s.public_ts_utc} title={`${s.public_ts_utc} UTC`}>
                  {ago(lang, s.public_ts_utc, now)} · {s.source}{s.fresh && <b className="new"> {t.live.new}</b>}
                </time>
                <a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a>
                <span className="tag"><i className="key-rect" style={{ background: color(s.narrative) }} />{NARR_LABEL[s.narrative] ?? s.narrative}</span>
                {s.assets?.map((a) => <span key={a} className="tag asset">{a}</span>)}
                {s.finbert_sentiment != null && <span className={`score num ${s.finbert_sentiment < 0 ? 'neg' : 'pos'}`}>FinBERT {fmt(lang, s.finbert_sentiment, 2, { signed: true })}</span>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
