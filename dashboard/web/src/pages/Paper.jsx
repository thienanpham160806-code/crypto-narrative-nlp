import { useEffect, useRef } from 'react'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import { useT } from '../i18n.js'
import { useData } from '../data.js'

/** Toàn văn bài nghiên cứu (paper/paper.md do nhóm viết, điền số liệu rồi chuyển sang HTML lúc export). */
export default function Paper() {
  const { lang } = useT()
  const { data, error } = useData('paper')
  const root = useRef(null)
  useEffect(() => {
    root.current?.querySelectorAll('.eq-tex').forEach(el =>
      katex.render(el.dataset.tex, el, { displayMode: true, throwOnError: false }))
  }, [data])
  if (error) return <div className="empty">{lang === 'vi' ? 'Chưa xuất bài báo.' : 'Paper not exported yet.'}</div>
  if (!data) return null
  return (
    <article className="paper" ref={root}>
      <p className="note">
        {lang === 'vi' ? 'Bài viết bằng tiếng Việt, tài liệu tham khảo theo APA 7. ' : 'This paper is written in Vietnamese; references follow APA 7. '}
        <a href="/paper.docx" download>{lang === 'vi' ? 'Tải bản Word (.docx)' : 'Download Word (.docx)'}</a>
      </p>
      <div dangerouslySetInnerHTML={{ __html: data.html }} />
    </article>
  )
}
