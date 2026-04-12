import type { Chapter } from '../../api'
import { useWorldContext } from '../../context/WorldContext'

export default function ChapterItem({ chapter }: { chapter: Chapter }) {
  const { activeChapterId, selectChapter, chapterLoading, scriptedChapterIds } = useWorldContext()
  const isActive = activeChapterId === chapter.id
  const hasScript = scriptedChapterIds.has(chapter.id)

  return (
    <button
      onClick={() => !chapterLoading && selectChapter(chapter.id)}
      disabled={chapterLoading}
      style={{
        width: '100%',
        display: 'block',
        padding: '6px 14px 6px 26px',
        border: 'none',
        background: isActive ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
        cursor: chapterLoading ? 'wait' : 'pointer',
        textAlign: 'left',
        transition: 'background 0.15s',
        borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
      }}
      onMouseEnter={e => {
        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'var(--bg-hover)'
      }}
      onMouseLeave={e => {
        if (!isActive) (e.currentTarget as HTMLElement).style.background = isActive ? 'rgba(99, 102, 241, 0.2)' : 'transparent'
      }}
    >
      <div style={{
        fontSize: '11px',
        fontWeight: isActive ? 600 : 400,
        color: isActive ? 'var(--accent-hover)' : 'var(--text-secondary)',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
      }}>
        <span style={{
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          flex: 1,
        }}>
          {chapter.title}
        </span>
        {hasScript && (
          <span style={{
            flexShrink: 0,
            fontSize: '8px',
            fontWeight: 700,
            color: 'var(--accent)',
            background: 'rgba(99, 102, 241, 0.12)',
            padding: '1px 4px',
            borderRadius: '3px',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}>
            Script
          </span>
        )}
      </div>
      {chapter.chapter_summary && (
        <div style={{
          fontSize: '10px',
          color: 'var(--text-muted)',
          marginTop: '1px',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}>
          {chapter.chapter_summary.slice(0, 60)}
        </div>
      )}
    </button>
  )
}
