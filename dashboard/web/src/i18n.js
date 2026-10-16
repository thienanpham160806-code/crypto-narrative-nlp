import { createContext, useContext } from 'react'

const T = {
  vi: {
    brandSub: 'Narrative & sentiment từ tin tức · 2023–2026',
    tabs: { overview: 'Tổng quan', narratives: 'Narratives', sentiment: 'Sentiment', coins: 'Theo coin', models: 'Dự báo & kiểm định', timing: 'Timing accuracy', validation: 'Validation', live: 'Live' },
    range: 'Khoảng thời gian', all: 'Toàn mẫu', days: (n) => `${n} ngày`,
    coverage: (a, b) => `Độ phủ tin: ${a} / ${b} ngày`,
    bands: { train: 'Train', valid: 'Valid', test: 'Test (ngoài mẫu)' },
    view: { chart: 'Hình', table: 'Bảng' },
    keyJudgements: 'Nhận định chính',
    asOf: (d, n) => `Tính đến ${d} (UTC) · ${n} tin trong 7 ngày`,
    m: { dominant: 'Dominant narrative', intensity: 'Narrative intensity', sentiment: 'Overall sentiment', negAccel: 'Negative-news acceleration', volRisk: 'BTC volatility risk' },
    level: { low: 'Thấp', normal: 'Bình thường', high: 'Cao', elevated: 'Elevated', none: 'Chưa đủ dữ liệu' },
    volSrc: { forecast: 'RV dự báo h=1', realized: 'RV thực hiện (chưa có dự báo)' },
    pctile: (p) => `phân vị ${p} trong 365 ngày`,
    j: {
      dominant: (n, s) => `${n} dẫn dắt dòng tin: ${s} attention trong 7 ngày.`,
      sentiment: (v) => `Sentiment FinBERT trung bình ${v}.`,
      neg: (v) => v == null ? 'Chưa đủ 14 ngày có tin để đo tăng tốc tin xấu.' : `Tin xấu ${v} so với 7 ngày trước.`,
      vol: (l) => `Rủi ro biến động BTC: ${l}.`,
    },
    ex: {
      attention: ['Attention theo narrative', 'Attention mềm (xác suất zero-shot), trung bình 7 ngày, % tin'],
      sentiment: ['Sentiment tin tức', 'FinBERT, trung bình 7 ngày, [−1, 1]'],
      btc: ['Giá BTC', 'Giá đóng cửa ngày, USD, thang log'],
      vol: ['Biến động BTC', 'Realized volatility ngày (tổng bình phương log-return giờ), ×10⁴'],
      timing: ['Độ lệch giờ công bố theo nguồn', 'Trung vị |giờ đăng − giờ hệ thống thấy|, phút'],
      snippets: ['Tin đại diện', 'Tin có sentiment hoặc narrative rõ nhất mỗi ngày, giờ public_ts_utc'],
    },
    judgement: {
      attention: 'Vùng tô đậm là kỳ valid/test: topic model không được fit trên các kỳ này.',
      sentiment: 'Sentiment ngày chỉ dùng tin có public_ts_utc trong ngày đó (UTC).',
      vol: 'Mô hình dự báo chỉ dùng thông tin trước ngày dự báo.',
      timing: 'Lệch giờ lớn nghĩa là gán ngày bằng giờ "thấy tin" có thể trễ hơn ngày công bố thật.',
    },
    source: { gdelt: 'Nguồn: GDELT GKG (lô :00 mỗi giờ), tính toán của nhóm.', binance: 'Nguồn: Binance qua ccxt.', timing: 'Nguồn: GDELT seendate, RSS pubDate, SEC Accepted.' },
    noData: 'Chưa có dữ liệu cho phần này. Chạy lại pipeline khi bộ thu GKG xong.',
    pending: 'Chờ dữ liệu',
    sortBy: 'Sắp xếp theo',
    live: { title: 'Live: tin mới nhất (không thuộc kết quả nghiên cứu)', note: 'Bản demo sản phẩm. Điểm được chấm bằng cùng FinBERT và zero-shot narrative, nhưng không đưa vào chỉ số nghiên cứu.', updated: 'Cập nhật' },
  },
  en: {
    brandSub: 'Narrative & sentiment from news · 2023–2026',
    tabs: { overview: 'Overview', narratives: 'Narratives', sentiment: 'Sentiment', coins: 'By coin', models: 'Forecasts & tests', timing: 'Timing accuracy', validation: 'Validation', live: 'Live' },
    range: 'Range', all: 'Full sample', days: (n) => `${n} days`,
    coverage: (a, b) => `News coverage: ${a} / ${b} days`,
    bands: { train: 'Train', valid: 'Valid', test: 'Test (out-of-sample)' },
    view: { chart: 'Chart', table: 'Table' },
    keyJudgements: 'Key judgements',
    asOf: (d, n) => `As of ${d} (UTC) · ${n} stories in 7 days`,
    m: { dominant: 'Dominant narrative', intensity: 'Narrative intensity', sentiment: 'Overall sentiment', negAccel: 'Negative-news acceleration', volRisk: 'BTC volatility risk' },
    level: { low: 'Low', normal: 'Normal', high: 'High', elevated: 'Elevated', none: 'Insufficient data' },
    volSrc: { forecast: 'Forecast RV h=1', realized: 'Realized RV (no forecast yet)' },
    pctile: (p) => `${p}th percentile over 365 days`,
    j: {
      dominant: (n, s) => `${n} leads the news flow: ${s} attention over 7 days.`,
      sentiment: (v) => `Average FinBERT sentiment ${v}.`,
      neg: (v) => v == null ? 'Fewer than 14 news days, so negative-news acceleration is not measured.' : `Negative news ${v} versus the prior 7 days.`,
      vol: (l) => `BTC volatility risk: ${l}.`,
    },
    ex: {
      attention: ['Attention by narrative', 'Soft attention (zero-shot probability), 7-day mean, % of stories'],
      sentiment: ['News sentiment', 'FinBERT, 7-day mean, [−1, 1]'],
      btc: ['BTC price', 'Daily close, USD, log scale'],
      vol: ['BTC volatility', 'Daily realized volatility (sum of squared hourly log returns), ×10⁴'],
      timing: ['Publication-time gap by source', 'Median |published − first seen|, minutes'],
      snippets: ['Representative stories', 'Stories with the clearest sentiment or narrative each day, at public_ts_utc'],
    },
    judgement: {
      attention: 'Shaded spans are valid/test: the topic models were never fitted on them.',
      sentiment: 'Daily sentiment uses only stories whose public_ts_utc falls on that UTC day.',
      vol: 'Forecasts use only information available before the forecast date.',
      timing: 'A large gap means dating by "first seen" can lag the true publication day.',
    },
    source: { gdelt: 'Source: GDELT GKG (:00 batch each hour), authors’ calculations.', binance: 'Source: Binance via ccxt.', timing: 'Source: GDELT seendate, RSS pubDate, SEC Accepted.' },
    noData: 'No data for this section yet. Re-run the pipeline once GKG collection finishes.',
    pending: 'Awaiting data',
    sortBy: 'Sort by',
    live: { title: 'Live: latest stories (not part of the research results)', note: 'Product demo. Scored with the same FinBERT and zero-shot narrative model, but never fed into the research indices.', updated: 'Updated' },
  },
}

export const NARR_LABEL = {
  regulation: 'Regulation', etf_institutional: 'ETF / institutional', security_hacks: 'Security / hacks',
  stablecoins: 'Stablecoins', defi: 'DeFi', ai_tokens: 'AI tokens', macro_monetary: 'Macro / monetary',
  price_speculation: 'Price / speculation', other: 'Other',
}

export const LangCtx = createContext({ lang: 'vi', t: T.vi })
export const useT = () => useContext(LangCtx)
export const dict = (lang) => T[lang]

export function fmt(lang, v, digits = 2, { signed = false, pct = false } = {}) {
  if (v == null || Number.isNaN(v)) return '–'
  const x = pct ? v * 100 : v
  const s = new Intl.NumberFormat(lang === 'vi' ? 'vi-VN' : 'en-US', {
    minimumFractionDigits: digits, maximumFractionDigits: digits, signDisplay: signed ? 'exceptZero' : 'auto',
  }).format(x)
  return (pct ? `${s}%` : s).replace('-', '−')
}
