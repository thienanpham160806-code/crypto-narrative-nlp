import { useT, fmt } from '../i18n.js'
import { useData } from '../data.js'
import Exhibit from '../Exhibit.jsx'
import Table from '../Table.jsx'

const L = {
  vi: {
    cov: ['Độ phủ dữ liệu cho mô hình', 'Số ngày có tin và có FinBERT, số ngày dùng được cho phát triển và test'],
    oos: ['So sánh ngoài mẫu: market-only vs market+text', 'RMSE và R² ngoài mẫu (Campbell–Thompson), walk-forward'],
    wald: ['Bất đối xứng tin xấu / tin tốt (RQ2)', 'Wald H₀: β⁻ = β⁺ trong hồi quy dự báo HAC'],
    granger: ['Lead-lag sentiment ↔ thị trường (RQ4)', 'VAR/Granger hai chiều; p đã hiệu chỉnh Holm và BH'],
    jCov: 'Mô hình chỉ kết luận được khi đủ ngày có tin; khi độ phủ thấp, các bảng dưới chỉ là kiểm tra pipeline.',
    jOos: 'R² ngoài mẫu dương nghĩa là text cải thiện dự báo so với benchmark; cần thêm kiểm định DM/Clark–West để kết luận.',
    jWald: 'p nhỏ nghĩa là tin xấu và tin tốt có hệ số khác nhau; xem dấu của β⁻ và β⁺ để biết bên nào mạnh hơn.',
    jGranger: 'Kết luận "pending" nghĩa là chưa đủ 30 ngày liên tục để chạy VAR.',
    src: 'Nguồn: outputs/tables/real (mô hình của Codex trên text_daily thật).',
  },
  en: {
    cov: ['Model data coverage', 'Days with news and FinBERT, days usable for development and test'],
    oos: ['Out-of-sample: market-only vs market+text', 'RMSE and out-of-sample R² (Campbell–Thompson), walk-forward'],
    wald: ['Bad-news / good-news asymmetry (RQ2)', 'Wald H₀: β⁻ = β⁺ in HAC predictive regressions'],
    granger: ['Sentiment ↔ market lead-lag (RQ4)', 'Two-way VAR/Granger; Holm and BH adjusted p'],
    jCov: 'Models only support conclusions with enough news days; at low coverage the tables below only check the pipeline.',
    jOos: 'Positive out-of-sample R² means text beats the benchmark; DM/Clark–West tests decide significance.',
    jWald: 'A small p means bad and good news carry different coefficients; the signs of β⁻ and β⁺ show which is stronger.',
    jGranger: '"Pending" means fewer than 30 contiguous days, so the VAR was not run.',
    src: 'Source: outputs/tables/real (Codex models on the real text_daily).',
  },
}

const p = (lang) => (v) => (v == null ? '–' : v < 0.001 ? (lang === 'vi' ? '<0,001' : '<0.001') : fmt(lang, v, 3))

export default function Models() {
  const { lang } = useT()
  const { data } = useData('models')
  const l = L[lang], f3 = (v) => fmt(lang, v, 3), pv = p(lang)
  const m = data ?? {}
  return (
    <div className="exhibits full">
      <Exhibit no="5.1" title={l.cov[0]} sub={l.cov[1]} span2 judgement={l.jCov} source={l.src}
        table={<Table rows={m.coverage ?? []} cols={[{ key: 'asset', label: 'Asset' }, { key: 'news_days', label: 'News days', num: true },
          { key: 'pct_days_with_news', label: '% days', num: true, format: (v) => fmt(lang, v, 1) }, { key: 'finbert_days', label: 'FinBERT days', num: true },
          { key: 'model_development_days', label: 'Dev days', num: true }, { key: 'model_test_days', label: 'Test days', num: true }]} />} />
      <Exhibit no="5.2" title={l.oos[0]} sub={l.oos[1]} span2 judgement={l.jOos} source={l.src}
        table={<Table rows={m.oos ?? []} cols={[{ key: 'asset', label: 'Asset' }, { key: 'target', label: 'Target' }, { key: 'horizon', label: 'h', num: true },
          { key: 'model', label: 'Model' }, { key: 'version', label: 'Version' }, { key: 'nobs', label: 'n', num: true },
          { key: 'rmse', label: 'RMSE', num: true, format: (v) => fmt(lang, v, 4) }, { key: 'r2_oos_ct', label: 'R²oos', num: true, format: f3 }]} />} />
      <Exhibit no="5.3" title={l.wald[0]} sub={l.wald[1]} judgement={l.jWald} source={l.src}
        table={<Table rows={m.wald ?? []} cols={[{ key: 'asset', label: 'Asset' }, { key: 'horizon', label: 'h', num: true },
          { key: 'beta_neg', label: 'β⁻', num: true, format: (v) => fmt(lang, v, 4) }, { key: 'beta_pos', label: 'β⁺', num: true, format: (v) => fmt(lang, v, 4) },
          { key: 'nobs', label: 'n', num: true }, { key: 'pvalue', label: 'p', num: true, format: pv }, { key: 'p_holm', label: 'p Holm', num: true, format: pv }]} />} />
      <Exhibit no="5.4" title={l.granger[0]} sub={l.granger[1]} judgement={l.jGranger} source={l.src}
        table={<Table rows={m.granger ?? []} cols={[{ key: 'asset', label: 'Asset' }, { key: 'outcome', label: 'Outcome' }, { key: 'nobs', label: 'n', num: true },
          { key: 'pvalue', label: 'p', num: true, format: pv }, { key: 'p_bh', label: 'p BH', num: true, format: pv }, { key: 'conclusion', label: 'Conclusion' }]} />} />
    </div>
  )
}
