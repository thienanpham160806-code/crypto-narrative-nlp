import { useT, fmt } from '../i18n.js'
import Exhibit, { Legend } from '../Exhibit.jsx'
import TimeChart from '../charts/TimeChart.jsx'
import Table from '../Table.jsx'
import { useRange } from './Overview.jsx'

const L = {
  vi: {
    three: ['Ba thước đo sentiment', 'FinBERT (transformer), Loughran–McDonald (từ điển tài chính), Harvard IV-4 (từ điển tổng quát); trung bình 7 ngày'],
    posneg: ['Tin tốt và tin xấu', 'pos_sent = mean(max(s,0)), neg_sent = mean(max(−s,0)); trung bình 7 ngày'],
    dis: ['Disagreement', '√(1 − A²), A = (N⁺ − N⁻)/(N⁺ + N⁻) theo nhãn FinBERT (Antweiler & Frank 2004); 0 = đồng thuận, 1 = chia đôi'],
    ucry: ['Crypto uncertainty (UCRY)', 'Lucey et al. (2022), chỉ số tuần, dùng từ ngày sau khi tuần kết thúc; có đến 2024-12'],
    jThree: 'Nếu các đường đi cùng chiều, ba phương pháp đo cùng một tín hiệu; RQ1 hỏi đường nào giải thích giá tốt hơn.',
    jPosNeg: 'Tách tin tốt và tin xấu để kiểm định bất đối xứng (RQ2): tin xấu có tác động mạnh hơn không.',
    jDis: 'Bất đồng cao nghĩa là tin cùng ngày kéo về hai phía; có thể đi trước biến động lớn.',
    jUcry: 'Biến kiểm soát cho bất định chung; mô hình có UCRY chỉ chạy trên đoạn có dữ liệu.',
    ucrySrc: 'Nguồn: Lucey, Vigne, Yarovaya & Wang (2022), sites.google.com/view/cryptocurrency-indices.',
  },
  en: {
    three: ['Three sentiment measures', 'FinBERT (transformer), Loughran–McDonald (finance dictionary), Harvard IV-4 (general dictionary); 7-day mean'],
    posneg: ['Good and bad news', 'pos_sent = mean(max(s,0)), neg_sent = mean(max(−s,0)); 7-day mean'],
    dis: ['Disagreement', '√(1 − A²), A = (N⁺ − N⁻)/(N⁺ + N⁻) on FinBERT labels (Antweiler & Frank 2004); 0 = consensus, 1 = split'],
    ucry: ['Crypto uncertainty (UCRY)', 'Lucey et al. (2022), weekly, usable from the day after each week ends; available to 2024-12'],
    jThree: 'Lines moving together measure one signal; RQ1 asks which explains prices better.',
    jPosNeg: 'Splitting good and bad news tests asymmetry (RQ2): does bad news hit harder?',
    jDis: 'High disagreement means same-day news pulls both ways; it may precede large moves.',
    jUcry: 'A control for general uncertainty; models with UCRY run only where it exists.',
    ucrySrc: 'Source: Lucey, Vigne, Yarovaya & Wang (2022), sites.google.com/view/cryptocurrency-indices.',
  },
}

export default function Sentiment() {
  const { t, lang, rows, splits } = useT()
  const view = useRange(rows)
  const l = L[lang], s2 = (v) => fmt(lang, v, 2, { signed: true }), d2 = (v) => fmt(lang, v, 2)
  const three = [
    { key: 'sent_finbert_7d', label: 'FinBERT', color: 'var(--s1)' },
    { key: 'sent_lm_7d', label: 'Loughran–McDonald', color: 'var(--s2)' },
    { key: 'sent_hv_7d', label: 'Harvard IV-4', color: 'var(--s3)' },
  ]
  const pn = [{ key: 'pos_sent_7d', label: 'pos_sent', color: 'var(--s6)' }, { key: 'neg_sent_7d', label: 'neg_sent', color: 'var(--s8)' }]
  const uc = [{ key: 'ucry_policy', label: 'UCRY Policy', color: 'var(--s7)' }, { key: 'ucry_price', label: 'UCRY Price', color: 'var(--s4)' }]
  const tbl = (series, f) => <Table rows={view} cols={[{ key: 'date', label: 'Date (UTC)' }, ...series.map((s) => ({ key: s.key, label: s.label, num: true, format: f }))]} />
  return (
    <div className="exhibits full">
      <Exhibit no="3.1" title={l.three[0]} sub={l.three[1]} span2 judgement={l.jThree} source={t.source.gdelt}
        legend={<Legend items={three} kind="line" />} chart={<TimeChart rows={view} series={three} splits={splits} height={280} yFormat={s2} />} table={tbl(three, s2)} />
      <Exhibit no="3.2" title={l.posneg[0]} sub={l.posneg[1]} judgement={l.jPosNeg} source={t.source.gdelt}
        legend={<Legend items={pn} kind="line" />} chart={<TimeChart rows={view} series={pn} splits={splits} yFormat={d2} />} table={tbl(pn, d2)} />
      <Exhibit no="3.3" title={l.dis[0]} sub={l.dis[1]} judgement={l.jDis} source={t.source.gdelt}
        chart={<TimeChart rows={view} series={[{ key: 'disagreement_7d', label: 'Disagreement 7d', color: 'var(--s5)' }]} splits={splits} yFormat={d2} />}
        table={tbl([{ key: 'disagreement', label: 'Disagreement' }], d2)} />
      <Exhibit no="3.4" title={l.ucry[0]} sub={l.ucry[1]} span2 judgement={l.jUcry} source={l.ucrySrc}
        legend={<Legend items={uc} kind="line" />} chart={<TimeChart rows={view} series={uc} splits={splits} yFormat={(v) => fmt(lang, v, 0)} />}
        table={tbl(uc, (v) => fmt(lang, v, 1))} />
    </div>
  )
}
