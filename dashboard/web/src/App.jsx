import { useEffect, useMemo, useState } from 'react'
import { LangCtx, dict } from './i18n.js'
import { useData, day, rolling } from './data.js'
import Overview from './pages/Overview.jsx'
import Narratives from './pages/Narratives.jsx'
import Sentiment from './pages/Sentiment.jsx'
import Coins from './pages/Coins.jsx'
import Models from './pages/Models.jsx'
import Timing from './pages/Timing.jsx'
import Validation from './pages/Validation.jsx'
import Live from './pages/Live.jsx'

const PAGES = { overview: Overview, narratives: Narratives, sentiment: Sentiment, coins: Coins, models: Models, timing: Timing, validation: Validation, live: Live }
const RANGES = [30, 90, 365, 'all']

const store = {
  get: (k) => { try { return localStorage.getItem(k) } catch { return null } },
  set: (k, v) => { try { localStorage.setItem(k, v) } catch { /* bộ nhớ trình duyệt bị chặn */ } },
}

function useHash() {
  const read = () => (location.hash.slice(2) in PAGES ? location.hash.slice(2) : 'overview')
  const [page, setPage] = useState(read)
  useEffect(() => {
    const on = () => { setPage(read()); window.scrollTo(0, 0) }
    addEventListener('hashchange', on)
    return () => removeEventListener('hashchange', on)
  }, [])
  return page
}

export default function App() {
  const [lang, setLang] = useState(() => (store.get('lang') === 'en' ? 'en' : 'vi'))
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'))
  const [range, setRange] = useState(() => { const r = store.get('range'); return r === 'all' ? 'all' : +r || 'all' })
  const page = useHash()
  const t = dict(lang)
  const meta = useData('meta').data
  const daily = useData('daily').data

  useEffect(() => { document.documentElement.lang = lang; store.set('lang', lang) }, [lang])
  useEffect(() => { document.documentElement.dataset.theme = theme; store.set('theme', theme) }, [theme])
  useEffect(() => { store.set('range', String(range)) }, [range])
  useEffect(() => { document.title = `${t.tabs[page]} · Crypto Narrative Report` }, [page, t])

  const rows = useMemo(() => {
    if (!daily || !meta) return []
    const r = daily.map((d) => ({ ...d, t: day(d.date) }))
    const keys = ['sent_finbert', 'sent_lm', 'sent_hv', 'pos_sent', 'neg_sent', 'disagreement', 'n_docs',
      ...meta.narratives.flatMap((k) => [`soft_attention_${k}`, `attention_${k}`])]
    for (const k of keys) rolling(r, k).forEach((v, i) => { r[i][`${k}_7d`] = v })
    return r
  }, [daily, meta])

  const splits = meta && { valid: new Date(meta.split.train_end + 'T00:00:00Z'), test: new Date(meta.split.valid_end + 'T00:00:00Z') }
  // ngày cuối có tin: các khoảng thời gian tính lùi từ đây, không từ cuối lịch
  const end = useMemo(() => [...rows].reverse().find((r) => r.n_docs > 0)?.t, [rows])
  const Page = PAGES[page]

  return (
    <LangCtx.Provider value={{ lang, t, meta, rows, range, splits, end }}>
      <header className="topbar">
        <div className="topbar-in">
          <div className="brand">Crypto Narrative Report<small>{t.brandSub}</small></div>
          <nav className="tabs" aria-label="Sections">
            {Object.keys(PAGES).map((k) => (
              <a key={k} href={`#/${k}`} aria-current={page === k ? 'page' : undefined}>{t.tabs[k]}</a>
            ))}
          </nav>
          <div className="toggles">
            <div className="seg" role="group" aria-label="Language">
              {['vi', 'en'].map((l) => <button key={l} aria-pressed={lang === l} onClick={() => setLang(l)}>{l.toUpperCase()}</button>)}
            </div>
            <div className="seg" role="group" aria-label="Theme">
              <button aria-pressed={theme === 'light'} onClick={() => setTheme('light')}>{lang === 'vi' ? 'Sáng' : 'Light'}</button>
              <button aria-pressed={theme === 'dark'} onClick={() => setTheme('dark')}>{lang === 'vi' ? 'Tối' : 'Dark'}</button>
            </div>
          </div>
        </div>
      </header>
      <main className="page">
        {page !== 'live' && (
          <div className="filters">
            <span className="label">{t.range}</span>
            <div className="chips" role="group" aria-label={t.range}>
              {RANGES.map((r) => (
                <button key={r} aria-pressed={range === r} onClick={() => setRange(r)}>{r === 'all' ? t.all : t.days(r)}</button>
              ))}
            </div>
            <span className="legend-bands">
              <span><i style={{ background: 'var(--band-valid)' }} />{t.bands.valid}</span>
              <span><i style={{ background: 'var(--band-test)' }} />{t.bands.test}</span>
            </span>
            {meta && <span className="coverage">{t.coverage(meta.news_days, meta.calendar_days).split(':')[0]}: <strong>{meta.news_days} / {meta.calendar_days}</strong></span>}
          </div>
        )}
        <Page />
      </main>
    </LangCtx.Provider>
  )
}
