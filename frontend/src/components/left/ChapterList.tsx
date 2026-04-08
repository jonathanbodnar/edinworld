import { useEffect, useState } from 'react'
import type { Chapter } from '../../api'
import { api } from '../../api'
import ChapterItem from './ChapterItem'

export default function ChapterList({ epochId }: { epochId: string }) {
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getChapters(epochId)
      .then(setChapters)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [epochId])

  if (loading) {
    return (
      <div style={{ padding: '6px 14px 8px 24px', color: 'var(--text-muted)', fontSize: '11px' }}>
        Loading...
      </div>
    )
  }

  if (chapters.length === 0) {
    return (
      <div style={{ padding: '6px 14px 8px 24px', color: 'var(--text-muted)', fontSize: '11px' }}>
        No chapters
      </div>
    )
  }

  return (
    <div style={{ paddingBottom: '2px' }}>
      {chapters.map(chapter => (
        <ChapterItem key={chapter.id} chapter={chapter} />
      ))}
    </div>
  )
}
