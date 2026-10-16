import { useT, fmt } from '../i18n.js'
import { useData } from '../data.js'
import Exhibit from '../Exhibit.jsx'
import Bars from '../charts/Bars.jsx'
import Table from '../Table.jsx'

const L = {
  vi: {
    intro: 'Đúng ngày ra công chúng mới đánh giá được tác động của tin. Mỗi tin được gán ngày bằng public_ts_utc = min(giờ đăng hợp lệ, giờ hệ thống thấy). Giờ đăng hợp lệ khi không sau giờ thấy và không sớm hơn quá 48 giờ.',
    acc: ['Độ chính xác timestamp theo nguồn', '% có giờ, trung vị |lệch|, % lệch > 1 giờ, % lệch sang ngày khác'],
    shift: ['Tin bị đổi ngày nếu dùng sai đồng hồ', '% cặp có ngày UTC khác nhau giữa hai đồng hồ'],
    corpus: ['Thống kê corpus', 'Số tin, tỷ lệ trùng, ngày có tin, tỷ lệ gắn mã coin theo nguồn'],
    jAcc: 'Lệch nhỏ (vài phút) nghĩa là giờ GDELT thấy tin gần giờ đăng; lệch lớn nghĩa là phải ưu tiên giờ đăng của trang.',
    jShift: 'Với SEC, giờ Accepted (New York) đổi sang UTC có thể sang ngày hôm sau so với file_date; dùng file_date sẽ gán sai ngày.',
    jCorpus: 'dup_rate là tỷ lệ bản trùng bị loại; chỉ bản công bố sớm nhất đi vào chỉ số ngày.',
  },
  en: {
    intro: 'Impact can only be measured on the day news became public. Each story is dated by public_ts_utc = min(valid published time, first-seen time). Published time is valid when it is not after first seen and not more than 48 hours earlier.',
    acc: ['Timestamp accuracy by source', '% with time, median |gap|, % gap > 1 hour, % moved to another day'],
    shift: ['Stories re-dated by the wrong clock', '% of pairs whose UTC day differs between the two clocks'],
    corpus: ['Corpus statistics', 'Stories, duplicate rate, news days and coin-tag share by source'],
    jAcc: 'A small gap (minutes) means GDELT sees stories close to publication; a large gap means the site’s own time must win.',
    jShift: 'For SEC, Accepted time (New York) converted to UTC can fall on the day after file_date; using file_date mis-dates filings.',
    jCorpus: 'dup_rate is the share of removed duplicates; only the earliest copy enters the daily index.',
  },
}

export default function Timing() {
  const { t, lang } = useT()
  const { data } = useData('timing')
  const l = L[lang], f1 = (v) => fmt(lang, v, 1)
  const acc = data?.accuracy ?? []
  return (
    <div className="exhibits full">
      <p className="prose note" style={{ gridColumn: '1 / -1', margin: 0 }}>{l.intro}</p>
      <Exhibit no="6.1" title={l.acc[0]} sub={l.acc[1]} span2 judgement={l.jAcc} source={t.source.timing}
        table={<Table rows={acc} cols={[{ key: 'source', label: 'Source' }, { key: 'comparison', label: 'Comparison' }, { key: 'n_docs', label: 'Docs', num: true },
          { key: 'n_pairs', label: 'Pairs', num: true }, { key: 'pct_has_time', label: '% with time', num: true, format: f1 },
          { key: 'median_lag_min', label: 'Median lag (min)', num: true, format: f1 }, { key: 'median_abs_lag_min', label: 'Median |lag|', num: true, format: f1 },
          { key: 'p90_abs_lag_min', label: 'P90 |lag|', num: true, format: f1 }, { key: 'pct_abs_gt_1h', label: '% > 1h', num: true, format: f1 },
          { key: 'pct_day_shift', label: '% day shift', num: true, format: f1 }]} />} />
      <Exhibit no="6.2" title={l.shift[0]} sub={l.shift[1]} judgement={l.jShift} source={t.source.timing}
        chart={<Bars rows={acc.filter((r) => r.pct_day_shift != null).map((r) => ({ label: `${r.source}`, value: r.pct_day_shift, note: r.comparison }))}
          format={(v) => `${fmt(lang, v, 1)}%`} color="var(--s2)" />}
        table={<Table rows={acc} cols={[{ key: 'source', label: 'Source' }, { key: 'comparison', label: 'Comparison' }, { key: 'pct_day_shift', label: '% day shift', num: true, format: f1 }]} />} />
      <Exhibit no="6.3" title={l.corpus[0]} sub={l.corpus[1]} judgement={l.jCorpus}
        table={<Table rows={data?.corpus ?? []} cols={[{ key: 'source', label: 'Source' }, { key: 'lang', label: 'Lang' }, { key: 'n_docs', label: 'Docs', num: true },
          { key: 'n_canonical', label: 'Canonical', num: true }, { key: 'dup_rate', label: 'Dup %', num: true, format: (v) => fmt(lang, v * 100, 1) },
          { key: 'days_with_docs', label: 'Days', num: true }, { key: 'pct_any_asset', label: '% tagged', num: true, format: f1 }]} />} />
    </div>
  )
}
