import { useState } from 'react'
import { useT, fmt, NARR_LABEL } from '../i18n.js'
import { useData } from '../data.js'
import Exhibit, { Legend } from '../Exhibit.jsx'
import TimeChart from '../charts/TimeChart.jsx'
import Table from '../Table.jsx'
import Snippets from './Snippets.jsx'
import { narrSeries, useRange } from './Overview.jsx'

const L = {
  vi: {
    stack: ['Attention mềm theo narrative', 'Tổng 8 narrative = 100%. Bấm chú giải để ẩn/hiện.'],
    hardSoft: ['Attention cứng và mềm', 'Cứng: % tin có nhãn narrative đó. Mềm: trung bình xác suất. Trung bình 7 ngày.'],
    taxonomy: ['Taxonomy: tỷ trọng theo phương pháp', '% tin tiếng Anh (không SEC); đồng thuận = % tin zero-shot gán k mà LDA/BERTopic cũng gán k'],
    topics: ['Topic của LDA và BERTopic', 'Fit trên train; topic → narrative theo embedding top-10 từ'],
    jTax: 'LDA và BERTopic học chủ đề không giám sát nên dồn tin vào ít narrative; zero-shot phân bố đều hơn. Đây là lý do zero-shot là phương pháp chính.',
    jHS: 'Hai đường gần nhau nghĩa là nhãn cứng không làm méo tỷ trọng; lệch xa nghĩa là nhiều tin mơ hồ giữa các narrative.',
  },
  en: {
    stack: ['Soft attention by narrative', 'The 8 narratives sum to 100%. Click the legend to hide or show.'],
    hardSoft: ['Hard vs soft attention', 'Hard: % of stories labelled k. Soft: mean probability. 7-day mean.'],
    taxonomy: ['Taxonomy: share by method', '% of English news stories (no SEC); agreement = % of zero-shot k stories that LDA/BERTopic also label k'],
    topics: ['LDA and BERTopic topics', 'Fitted on train; topic → narrative by embedding the top-10 words'],
    jTax: 'Unsupervised LDA and BERTopic pile stories into few narratives; zero-shot spreads them more evenly. That is why zero-shot is the primary method.',
    jHS: 'Close lines mean hard labels do not distort shares; a wide gap means many stories sit between narratives.',
  },
}

export default function Narratives() {
  const { t, lang, meta, rows, splits } = useT()
  const { data } = useData('narratives')
  const [hidden, setHidden] = useState(new Set())
  const [focus, setFocus] = useState('regulation')
  const view = useRange(rows)
  if (!meta) return null
  const l = L[lang], pct = (v) => fmt(lang, v, 0, { pct: true })
  const all = narrSeries(meta)
  const shown = all.filter((s) => !hidden.has(s.key))
  const toggle = (k) => setHidden((h) => { const n = new Set(h); n.has(k) ? n.delete(k) : n.add(k); return n })
  const i = meta.narratives.indexOf(focus)
  const hs = [
    { key: `soft_attention_${focus}_7d`, label: `${NARR_LABEL[focus]} · soft`, color: all[i].color },
    { key: `attention_${focus}_7d`, label: `${NARR_LABEL[focus]} · hard`, color: 'var(--ink-2)' },
  ]
  return (
    <div className="exhibits full">
      <Exhibit no="2.1" title={l.stack[0]} sub={l.stack[1]} span2 source={t.source.gdelt} judgement={t.judgement.attention}
        legend={<Legend items={all} hidden={hidden} onToggle={toggle} />}
        chart={<TimeChart rows={view} series={shown} stacked splits={splits} height={300} yFormat={pct} />}
        table={<Table rows={view} cols={[{ key: 'date', label: t.col.date }, ...all.map((s) => ({ key: s.key, label: s.label, num: true, format: pct }))]} />} />
      <Exhibit no="2.2" title={l.hardSoft[0]} sub={l.hardSoft[1]} judgement={l.jHS} source={t.source.gdelt}
        legend={<>
          <div className="chips" role="group" aria-label="Narrative" style={{ marginBottom: 8, flexWrap: 'wrap' }}>
            {meta.narratives.map((k) => <button key={k} aria-pressed={focus === k} onClick={() => setFocus(k)}>{NARR_LABEL[k]}</button>)}
          </div>
          <Legend items={hs} kind="line" />
        </>}
        chart={<TimeChart rows={view} series={hs} splits={splits} yFormat={pct} />}
        table={<Table rows={view} cols={[{ key: 'date', label: t.col.date }, ...hs.map((s) => ({ key: s.key, label: s.label, num: true, format: pct }))]} />} />
      <Exhibit no="2.3" title={l.taxonomy[0]} sub={l.taxonomy[1]} judgement={l.jTax}
        table={<Table rows={data?.taxonomy ?? []} cols={[
          { key: 'narrative', label: 'Narrative', format: (v) => NARR_LABEL[v] ?? v },
          { key: 'share_zs', label: 'Zero-shot %', num: true, format: (v) => fmt(lang, v, 1) },
          { key: 'share_lda', label: 'LDA %', num: true, format: (v) => fmt(lang, v, 1) },
          { key: 'share_bt', label: 'BERTopic %', num: true, format: (v) => fmt(lang, v, 1) },
          { key: 'agree_lda_with_zs', label: 'LDA = ZS %', num: true, format: (v) => fmt(lang, v, 0) },
          { key: 'agree_bt_with_zs', label: 'BERTopic = ZS %', num: true, format: (v) => fmt(lang, v, 0) }]} />} />
      <Exhibit no="2.4" title={l.topics[0]} sub={l.topics[1]} span2
        table={<Table rows={data?.topics ?? []} cols={[{ key: 'method', label: t.col.method }, { key: 'topic', label: t.col.topic, num: true },
          { key: 'narrative', label: 'Narrative', format: (v) => NARR_LABEL[v] ?? v }, { key: 'top_words', label: t.col.words }]} />} />
      <Snippets no="2.5" limit={20} />
    </div>
  )
}
