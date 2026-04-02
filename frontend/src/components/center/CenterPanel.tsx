import { useChapterContext } from '../../context/ChapterContext'
import WorldPlaceholder from './WorldPlaceholder'
import ChapterOverlay from './ChapterOverlay'
import NarrationOverlay from './NarrationOverlay'

export default function CenterPanel() {
  const { chapterDetail, narration, loading } = useChapterContext()

  return (
    <div style={{
      position: 'relative',
      height: '100%',
      overflow: 'hidden',
      background: 'var(--bg-primary)',
    }}>
      <WorldPlaceholder />

      {loading && (
        <div style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(15, 17, 23, 0.8)',
          zIndex: 10,
        }}>
          <div style={{
            color: 'var(--accent)',
            fontSize: '14px',
            fontWeight: 500,
          }}>
            Loading chapter...
          </div>
        </div>
      )}

      {chapterDetail && !loading && (
        <>
          <ChapterOverlay chapter={chapterDetail} />
          {narration && <NarrationOverlay narration={narration} />}
        </>
      )}
    </div>
  )
}
