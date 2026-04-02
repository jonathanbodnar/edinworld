import { useChapterContext } from '../../context/ChapterContext'

export default function WorldPlaceholder() {
  const { activeChapterId } = useChapterContext()

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: `
        radial-gradient(ellipse at center, rgba(99, 102, 241, 0.08) 0%, transparent 70%),
        var(--bg-primary)
      `,
    }}>
      {!activeChapterId && (
        <div style={{ textAlign: 'center', maxWidth: '400px' }}>
          <div style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            border: '2px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px',
            background: 'var(--bg-secondary)',
          }}>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="1.5">
              <circle cx="12" cy="12" r="10" />
              <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
          </div>
          <h2 style={{
            fontSize: '18px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            marginBottom: '8px',
          }}>
            World Viewport
          </h2>
          <p style={{
            fontSize: '13px',
            color: 'var(--text-muted)',
            lineHeight: '1.6',
          }}>
            Select a chapter from the left panel to explore the ancient world. This space will render the interactive world environment.
          </p>
        </div>
      )}
    </div>
  )
}
