import { useT } from '../i18n.js'
import { useData } from '../data.js'

/** Toàn văn bài nghiên cứu (paper/paper.md do nhóm viết, chuyển sang HTML lúc export). */
export default function Paper() {
  const { lang } = useT()
  const { data, error } = useData('paper')
  if (error) return <div className="empty">{lang === 'vi' ? 'Chưa xuất bài báo.' : 'Paper not exported yet.'}</div>
  if (!data) return null
  return (
    <article className="paper">
      {lang === 'en' && <p className="note">This paper is written in Vietnamese; references follow APA 7.</p>}
      <div dangerouslySetInnerHTML={{ __html: data.html }} />
    </article>
  )
}
