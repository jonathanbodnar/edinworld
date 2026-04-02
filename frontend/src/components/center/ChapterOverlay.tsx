import type { ChapterDetail } from '../../api'

function formatYear(y: number | null): string {
  if (y === null) return '?'
  if (y < 0) return `${Math.abs(y)} BCE`
  return `${y} CE`
}

export default function ChapterOverlay({ chapter }: { chapter: ChapterDetail }) {
  return (
    <div style={{
      position: 'absolute',
      bottom: 0,
      left: 0,
      right: 0,
      background: 'linear-gradient(transparent, rgba(15, 17, 23, 0.95))',
      padding: '60px 32px 24px',
      pointerEvents: 'none',
    }}>
      <div style={{
        fontSize: '11px',
        color: 'var(--accent)',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        marginBottom: '6px',
      }}>
        {formatYear(chapter.time_start)} — {formatYear(chapter.time_end)}
      </div>

      <h2 style={{
        fontSize: '24px',
        fontWeight: 700,
        color: 'var(--text-primary)',
        marginBottom: '8px',
        lineHeight: 1.2,
      }}>
        {chapter.title}
      </h2>

      {chapter.chapter_summary && (
        <p style={{
          fontSize: '13px',
          color: 'var(--text-secondary)',
          lineHeight: 1.6,
          maxWidth: '600px',
        }}>
          {chapter.chapter_summary.slice(0, 300)}
          {chapter.chapter_summary.length > 300 && '...'}
        </p>
      )}

      {(chapter.actors.length > 0 || chapter.events.length > 0 || chapter.places.length > 0) && (
        <div style={{
          display: 'flex',
          gap: '16px',
          marginTop: '12px',
          flexWrap: 'wrap',
        }}>
          {chapter.actors.length > 0 && (
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {chapter.actors.length} actor{chapter.actors.length !== 1 && 's'}
            </span>
          )}
          {chapter.events.length > 0 && (
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {chapter.events.length} event{chapter.events.length !== 1 && 's'}
            </span>
          )}
          {chapter.places.length > 0 && (
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {chapter.places.length} place{chapter.places.length !== 1 && 's'}
            </span>
          )}
        </div>
      )}
    </div>
  )
}
