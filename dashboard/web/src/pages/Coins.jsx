import { useMemo } from 'react'
import { useT, fmt } from '../i18n.js'
import { useData, day } from '../data.js'
import Exhibit from '../Exhibit.jsx'
import Bars from '../charts/Bars.jsx'
import Table from '../Table.jsx'

const L = {
  vi: {
    count: ['Số tin theo coin', 'Tin gắn mã (regex ticker/tên coin), trong khoảng đang lọc'],
    sent: ['Sentiment theo coin', 'FinBERT trung bình, có trọng số theo số tin mỗi ngày'],
    jCount: 'BTC chiếm phần lớn tin; coin ít tin có chỉ số ngày nhiễu hơn, nên mô hình dùng ALL khi thiếu tin riêng.',
    jSent: 'So sánh mức sentiment giữa các coin; khác biệt nhỏ trên ít tin không đủ để kết luận.',
  },
  en: {
    count: ['Stories by coin', 'Stories tagged by ticker/name regex, within the selected range'],
    sent: ['Sentiment by coin', 'Mean FinBERT, weighted by daily story count'],
    jCount: 'BTC dominates coverage; thinly covered coins have noisier daily indices, so models fall back to ALL.',
    jSent: 'Compares sentiment levels across coins; small gaps on few stories are not conclusive.',
  },
}

export default function Coins() {
  const { t, lang, meta, range, end } = useT()
  const { data } = useData('assets')
  const l = L[lang]
  const agg = useMemo(() => {
    if (!data || !meta || !end) return []
    const from = range === 'all' ? null : new Date(end.getTime() - (range - 1) * 864e5)
    return meta.sample.assets.map((a) => {
      const r = data.filter((d) => d.asset === a && day(d.date) <= end && (!from || day(d.date) >= from))
      const n = r.reduce((s, d) => s + d.n_docs, 0)
      const w = r.filter((d) => d.sent_finbert != null)
      const sw = w.reduce((s, d) => s + d.n_docs, 0)
      return { asset: a, n_docs: n, days: r.length, sent: sw ? w.reduce((s, d) => s + d.sent_finbert * d.n_docs, 0) / sw : null }
    })
  }, [data, meta, range, end])
  const cols = [{ key: 'asset', label: 'Asset' }, { key: 'n_docs', label: 'n', num: true }, { key: 'days', label: 'Days', num: true },
    { key: 'sent', label: 'FinBERT', num: true, format: (v) => fmt(lang, v, 3, { signed: true }) }]
  return (
    <div className="exhibits full">
      <Exhibit no="4.1" title={l.count[0]} sub={l.count[1]} judgement={l.jCount} source={t.source.gdelt}
        chart={<Bars rows={agg.map((r) => ({ label: r.asset, value: r.n_docs }))} format={(v) => fmt(lang, v, 0)} />} table={<Table rows={agg} cols={cols} />} />
      <Exhibit no="4.2" title={l.sent[0]} sub={l.sent[1]} judgement={l.jSent} source={t.source.gdelt}
        table={<Table rows={agg} cols={cols} />} />
    </div>
  )
}
