import { createContext, useContext } from 'react'

const T = {
  vi: {
    brandSub: 'Narrative & sentiment từ tin tức · 2023–2026',
    tabs: { overview: 'Tổng quan', narratives: 'Narratives', sentiment: 'Sentiment', coins: 'Theo coin', models: 'Dự báo & kiểm định', timing: 'Timing accuracy', validation: 'Validation', paper: 'Bài báo', live: 'Live' },
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
    noData: 'Không có quan sát nào trong khoảng thời gian này.',
    pending: 'Chờ dữ liệu',
    fcPending: 'Dự báo ngoài mẫu: đang chờ mô hình',
    modelPending: 'Chờ mô hình market+text của Codex: cần đủ ngày có tin trong kỳ valid và test.',
    status: { 'VAR pending: fewer than 30 contiguous daily observations': 'Chưa chạy VAR: ít hơn 30 ngày liên tục' },
    fan: { pred: 'Dự báo EN market+text', b50: 'Dải 50%', b90: 'Dải 90%', actual: 'RV thực hiện' },
    lagPending: (n) => `Chưa đo được độ lệch giờ đăng của tin báo (${n} cặp có giờ đăng). Đang hiện tỷ lệ đổi ngày của SEC.`,
    snapshot: (d, n) => `Bản chụp mô hình: tin đến ${d}, ${n} ngày có tin.`,
    col: { date: 'Ngày (UTC)', source: 'Nguồn', comparison: 'So sánh', docs: 'Số tin', pairs: 'Số cặp', asset: 'Tài sản', days: 'Số ngày',
      lang: 'Ngôn ngữ', canonical: 'Bản gốc', tagged: '% gắn mã', withTime: '% có giờ', medLag: 'Lệch trung vị (phút)', medAbs: '|Lệch| trung vị',
      p90: '|Lệch| P90', gt1h: '% > 1 giờ', dayShift: '% đổi ngày', method: 'Phương pháp', topic: 'Topic', words: 'Từ đặc trưng',
      target: 'Biến mục tiêu', model: 'Mô hình', version: 'Phiên bản', outcome: 'Biến kết quả', conclusion: 'Kết luận', task: 'Nhiệm vụ', newsDays: 'Ngày có tin', pctDays: '% ngày', fbDays: 'Ngày có FinBERT', devDays: 'Ngày phát triển', testDays: 'Ngày test' },
    sortBy: 'Sắp xếp theo',
    live: { title: 'Live: tin mới nhất (không thuộc kết quả nghiên cứu)', note: 'Bản demo sản phẩm. Điểm được chấm bằng cùng FinBERT và zero-shot narrative, nhưng không đưa vào chỉ số nghiên cứu.', updated: 'Cập nhật' },
  },
  en: {
    brandSub: 'Narrative & sentiment from news · 2023–2026',
    tabs: { overview: 'Overview', narratives: 'Narratives', sentiment: 'Sentiment', coins: 'By coin', models: 'Forecasts & tests', timing: 'Timing accuracy', validation: 'Validation', paper: 'Paper', live: 'Live' },
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
    noData: 'No observations in this range.',
    pending: 'Awaiting data',
    fcPending: 'Out-of-sample forecast: awaiting model',
    modelPending: 'Awaiting the market+text models: enough news days are needed in the valid and test periods.',
    status: {},
    fan: { pred: 'Forecast EN market+text', b50: '50% band', b90: '90% band', actual: 'Realized RV' },
    lagPending: (n) => `News publication-time gaps are not measured yet (${n} pairs with a published time). Showing SEC day shifts instead.`,
    snapshot: (d, n) => `Model snapshot: news through ${d}, ${n} news days.`,
    col: { date: 'Date (UTC)', source: 'Source', comparison: 'Comparison', docs: 'Stories', pairs: 'Pairs', asset: 'Asset', days: 'Days',
      lang: 'Language', canonical: 'Canonical', tagged: '% tagged', withTime: '% with time', medLag: 'Median lag (min)', medAbs: 'Median |lag|',
      p90: 'P90 |lag|', gt1h: '% > 1h', dayShift: '% day shift', method: 'Method', topic: 'Topic', words: 'Top words',
      target: 'Target', model: 'Model', version: 'Version', outcome: 'Outcome', conclusion: 'Conclusion', task: 'Task', newsDays: 'News days', pctDays: '% days', fbDays: 'FinBERT days', devDays: 'Dev days', testDays: 'Test days' },
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
