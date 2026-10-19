import { useT, fmt } from '../i18n.js'
import { useData } from '../data.js'
import Exhibit from '../Exhibit.jsx'
import Table from '../Table.jsx'

const L = {
  vi: {
    title: ['Kiểm định sentiment và narrative bằng nhãn tay (RQ1)', '300 tiêu đề ngẫu nhiên (seed 42) trước kỳ test, gán nhãn tay; accuracy và macro-F1'],
    j: 'Phương pháp có macro-F1 cao hơn đo đúng giọng điệu tin crypto hơn. Đây là bằng chứng trực tiếp cho RQ1, trước khi xét tác động lên giá.',
    empty: 'Chưa có nhãn tay. Nhóm cần gán nhãn data/interim/validation_sample.csv (cột label_sentiment, label_narrative) rồi chạy python -m features.validation.',
  },
  en: {
    title: ['Sentiment and narrative validation against hand labels (RQ1)', '300 random headlines (seed 42) before the test period, hand-labelled; accuracy and macro-F1'],
    j: 'Higher macro-F1 means the method reads crypto news tone more correctly. This is direct evidence for RQ1, before any price effect.',
    empty: 'No hand labels yet. Label data/interim/validation_sample.csv (label_sentiment, label_narrative), then run python -m features.validation.',
  },
}

export default function Validation() {
  const { t, lang } = useT()
  const { data } = useData('validation')
  const l = L[lang], f3 = (v) => fmt(lang, v, 3)
  return (
    <div className="exhibits full">
      <Exhibit no="7.1" title={l.title[0]} sub={l.title[1]} span2 judgement={l.j}
        table={data?.length ? <Table rows={data} cols={[{ key: 'task', label: t.col.task }, { key: 'method', label: t.col.method }, { key: 'n', label: 'n', num: true },
          { key: 'accuracy', label: 'Accuracy', num: true, format: f3 }, { key: 'macro_f1', label: 'Macro-F1', num: true, format: f3 }]} /> : <div className="empty">{l.empty}</div>} />
    </div>
  )
}
