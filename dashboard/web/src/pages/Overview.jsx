import { useMemo } from 'react'
import { useT, fmt, NARR_LABEL } from '../i18n.js'
import { useData, inRange, day } from '../data.js'
import Exhibit, { Legend } from '../Exhibit.jsx'
import TimeChart from '../charts/TimeChart.jsx'
import Bars from '../charts/Bars.jsx'
import Table from '../Table.jsx'
import Snippets from './Snippets.jsx'

export const COLORS = ['var(--s1)', 'var(--s2)', 'var(--s3)', 'var(--s4)', 'var(--s5)', 'var(--s6)', 'var(--s7)', 'var(--s8)']
const RISK_COLOR = { low: 'var(--st-good)', normal: 'var(--st-good)', elevated: 'var(--st-serious)', high: 'var(--st-critical)' }

export function narrSeries(meta, prefix = 'soft_attention_', suffix = '_7d') {
  return meta.narratives.map((k, i) => ({ key: `${prefix}${k}${suffix}`, label: NARR_LABEL[k], color: COLORS[i], narr: k }))
}

function RiskIcon({ level }) {
  // hình khác nhau theo mức, để không chỉ dựa vào màu
  const c = RISK_COLOR[level] ?? 'var(--muted)'
  if (level === 'high' || level === 'elevated') return <svg width="16" height="16" aria-hidden="true"><path d="M8 1.5 15 14.5H1z" fill={c} /></svg>
  return <svg width="16" height="16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill={c} /></svg>
}

function Judgements() {
  const { t, lang } = useT()
  const s = useData('summary').data
  if (!s || !s.as_of) return <aside className="judge"><h1>{t.keyJudgements}</h1><p className="note">{t.noData}</p></aside>
  const lvl = (v) => (v ? t.level[v] : t.level.none)
  const neg = s.neg_accel.value
  return (
    <aside className="judge">
      <h1>{t.keyJudgements}</h1>
      <p className="asof num">{t.asOf(s.as_of, s.n_docs_7d)}</p>
      <ul>
        <li>{t.j.dominant(NARR_LABEL[s.dominant.narrative], fmt(lang, s.dominant.share, 1, { pct: true }))}</li>
        <li>{t.j.sentiment(fmt(lang, s.sentiment.value, 2, { signed: true }))}</li>
        <li>{t.j.neg(neg == null ? null : fmt(lang, neg, 0, { signed: true, pct: true }))}</li>
        <li>{t.j.vol(lvl(s.vol_risk.level))}</li>
      </ul>
      <dl className="metrics">
        <div className="metric"><dt>{t.m.dominant}</dt><dd>{NARR_LABEL[s.dominant.narrative]}<small>{fmt(lang, s.dominant.share, 1, { pct: true })} attention · 7d</small></dd></div>
        <div className="metric"><dt>{t.m.intensity}</dt><dd>{lvl(s.intensity.level)}<small>z = {fmt(lang, s.intensity.z, 1, { signed: true })}</small></dd></div>
        <div className="metric"><dt>{t.m.sentiment}</dt><dd>{fmt(lang, s.sentiment.value, 2, { signed: true })}<small>FinBERT · 7d</small></dd></div>
        <div className="metric"><dt>{t.m.negAccel}</dt><dd>{fmt(lang, neg, 0, { signed: true, pct: true })}<small>neg_sent 7d / 7d</small></dd></div>
        <div className="metric"><dt>{t.m.volRisk}</dt><dd><span className="risk"><RiskIcon level={s.vol_risk.level} />{lvl(s.vol_risk.level)}</span>
          <small>{t.volSrc[s.vol_risk.source]}{s.vol_risk.percentile != null ? ` · ${t.pctile(Math.round(s.vol_risk.percentile * 100))}` : ''}</small></dd></div>
      </dl>
    </aside>
  )
}

export function useRange(rows) {
  const { range, end } = useT()
  return useMemo(() => inRange(rows.filter((r) => !end || r.t <= end), range, end), [rows, range, end])
}

export default function Overview() {
  const { t, lang, meta, rows, splits } = useT()
  const timing = useData('timing').data
  const fanData = useData('fan').data
  const ranged = useRange(rows)
  const view = useMemo(() => {
    const byDay = new Map((fanData ?? []).map((f) => [f.date.slice(0, 10), f]))
    return byDay.size ? ranged.map((r) => ({ ...r, ...byDay.get(r.date.slice(0, 10)) })) : ranged
  }, [ranged, fanData])
  if (!meta) return null
  const nar = narrSeries(meta)
  const pct = (v) => fmt(lang, v, 0, { pct: true })
  const acc = timing?.accuracy ?? []
  const lagRows = acc.filter((r) => r.median_abs_lag_min != null)
    .map((r) => ({ label: `${r.source} · n = ${r.n_pairs}`, value: r.median_abs_lag_min, note: r.comparison }))
  const shiftRows = acc.filter((r) => r.pct_day_shift != null).map((r) => ({ label: r.source, value: r.pct_day_shift, note: r.comparison }))
  const pairs = acc.filter((r) => r.source === 'gdelt').reduce((s, r) => s + (r.n_pairs ?? 0), 0)
  const hasFan = view.some((r) => r.fan_pred != null)
  const rv = (v) => fmt(lang, v * 1e4, 0)
  const fanSeries = [{ key: 'btc_rv', label: t.fan.actual, color: 'var(--s2)' }, ...(hasFan ? [{ key: 'fan_pred', label: t.fan.pred, color: 'var(--accent)', dash: true }] : [])]
  const fanBands = hasFan ? [
    { lo: 'fan_lo90', hi: 'fan_hi90', color: 'var(--accent)', opacity: 0.12, label: t.fan.b90 },
    { lo: 'fan_lo50', hi: 'fan_hi50', color: 'var(--accent)', opacity: 0.22, label: t.fan.b50 }] : []
  const tableCols = [{ key: 'date', label: t.col.date }, ...nar.map((s) => ({ key: s.key, label: s.label, num: true, format: pct }))]
  return (
    <div className="report">
      <Judgements />
      <div className="exhibits">
        <Exhibit no="1.1" title={t.ex.attention[0]} sub={t.ex.attention[1]} judgement={t.judgement.attention} source={t.source.gdelt}
          legend={<Legend items={nar} />}
          chart={<TimeChart rows={view} series={nar} stacked splits={splits} yFormat={pct} />}
          table={<Table rows={view} cols={tableCols} />} />
        <Exhibit no="1.2" title={`${t.ex.sentiment[0]} · ${t.ex.btc[0]}`} sub={`${t.ex.sentiment[1]}; ${t.ex.btc[1]}`}
          judgement={t.judgement.sentiment} source={`${t.source.gdelt} ${t.source.binance}`}
          chart={<>
            <TimeChart rows={view} height={150} splits={splits} series={[{ key: 'sent_finbert_7d', label: 'FinBERT 7d', color: 'var(--s1)' }]} yFormat={(v) => fmt(lang, v, 2, { signed: true })} />
            <TimeChart rows={view} height={150} splits={splits} log series={[{ key: 'btc_close', label: 'BTC', color: 'var(--s7)' }]} yFormat={(v) => fmt(lang, v / 1000, 0) + 'k'} />
          </>}
          table={<Table rows={view} cols={[{ key: 'date', label: t.col.date }, { key: 'sent_finbert', label: 'FinBERT', num: true, format: (v) => fmt(lang, v, 3) },
            { key: 'n_docs', label: 'n', num: true }, { key: 'btc_close', label: 'BTC close', num: true, format: (v) => fmt(lang, v, 0) }]} />} />
        <Exhibit no="1.3" title={t.ex.vol[0]} sub={hasFan ? t.ex.vol[1] : `${t.ex.vol[1]} · ${t.fcPending}`} judgement={t.judgement.vol} source={t.source.binance}
          legend={hasFan && <Legend items={[...fanSeries, ...fanBands.map((b) => ({ key: b.lo, label: b.label, color: b.color }))]} kind="line" />}
          chart={<TimeChart rows={view} splits={splits} series={fanSeries} bands={fanBands} yFormat={rv} testNote={hasFan ? null : t.fcPending} />}
          table={<Table rows={view} cols={[{ key: 'date', label: t.col.date }, { key: 'btc_rv', label: 'RV ×10⁴', num: true, format: (v) => fmt(lang, v * 1e4, 2) },
            ...(hasFan ? [{ key: 'fan_pred', label: t.fan.pred, num: true, format: (v) => fmt(lang, v * 1e4, 2) }] : [])]} />} />
        <Exhibit no="1.4" title={t.ex.timing[0]} sub={lagRows.length ? t.ex.timing[1] : t.lagPending(pairs)} judgement={t.judgement.timing} source={t.source.timing}
          chart={lagRows.length ? <Bars rows={lagRows} format={(v) => `${fmt(lang, v, 0)} min`} />
            : <Bars rows={shiftRows} format={(v) => `${fmt(lang, v, 1)}%`} color="var(--s2)" />}
          table={<Table rows={timing?.accuracy ?? []} cols={[{ key: 'source', label: t.col.source }, { key: 'comparison', label: t.col.comparison },
            { key: 'n_pairs', label: 'n', num: true }, { key: 'median_abs_lag_min', label: t.col.medAbs, num: true, format: (v) => fmt(lang, v, 0) },
            { key: 'pct_abs_gt_1h', label: t.col.gt1h, num: true, format: (v) => fmt(lang, v, 1) }, { key: 'pct_day_shift', label: t.col.dayShift, num: true, format: (v) => fmt(lang, v, 1) }]} />} />
        <Snippets no="1.5" />
      </div>
    </div>
  )
}

export { day }
