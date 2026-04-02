import type { Chapter } from '../../api'
import { useChapterContext } from '../../context/ChapterContext'

export default function ChapterItem({ chapter }: { chapter: Chapter }) {
  const { activeChapterId, selectChapter, loading } = useChapterContext()
  const isActive = activeChapterId === chapter.id

  return (
    <button
      onClick={() => !loading && selectChapter(chapter.id)}
      disabled={loading}
      style={{
        width: '100%',
        display: 'block',
        padding: '8px 16px 8px 28px',
        border: 'none',
        background: isActive ? 'var(--accent)' : 'transparent',
        cursor: loading ? 'wait' : 'pointer',
        textAlign: 'left',
        transition: 'background 0.15s',
        borderLeft: isActive ? '3px solid var(--accent-hover)' : '3px solid transparent',
      }}
      onMouseEnter={e => {
        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'var(--bg-hover)'
      }}
      onMouseLeave={e => {
        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'transparent'
      }}
    >
      <div style={{
        fontSize: '12px',
        fontWeight: isActive ? 600 : 400,
        color: isActive ? '#fff' : 'var(--text-primary)',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      }}>
        {chapter.title}
      </div>
      {chapter.chapter_summary && (
        <div style={{
          fontSize: '11px',
          color: isActive ? 'rgba(255,255,255,0.7)' : 'var(--text-muted)',
          marginTop: '2px',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}>
          {chapter.chapter_summary.slice(0, 80)}
        </div>
      )}
    </button>
  )
}
