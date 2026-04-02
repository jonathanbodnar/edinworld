import { useChapterContext } from '../../context/ChapterContext'
import ArtifactCard from './ArtifactCard'
import ImageCard from './ImageCard'

export default function ContextTab() {
  const { contexts, artifacts, images } = useChapterContext()

  const empty = contexts.length === 0 && artifacts.length === 0 && images.length === 0

  if (empty) {
    return (
      <div style={{
        padding: '24px 16px',
        color: 'var(--text-muted)',
        fontSize: '13px',
        textAlign: 'center',
      }}>
        No contextual data found for this chapter.
      </div>
    )
  }

  return (
    <div style={{ padding: '12px' }}>
      {contexts.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontSize: '11px',
            color: 'var(--text-muted)',
            fontWeight: 500,
            padding: '4px 4px 8px',
          }}>
            Contextual Statements ({contexts.length})
          </div>
          {contexts.map(ctx => (
            <div key={ctx.id} style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '12px',
              marginBottom: '8px',
            }}>
              <p style={{
                fontSize: '12px',
                color: 'var(--text-secondary)',
                lineHeight: 1.5,
              }}>
                {ctx.summary || 'No summary available'}
              </p>
              {ctx.artifact_description && (
                <p style={{
                  fontSize: '11px',
                  color: 'var(--text-muted)',
                  marginTop: '6px',
                  fontStyle: 'italic',
                }}>
                  {ctx.artifact_description}
                </p>
              )}
              <div style={{
                display: 'flex',
                justifyContent: 'flex-end',
                marginTop: '6px',
              }}>
                <span style={{
                  fontSize: '10px',
                  color: 'var(--accent)',
                  fontWeight: 600,
                }}>
                  {(ctx.relevance_weight * 100).toFixed(0)}% relevance
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {artifacts.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontSize: '11px',
            color: 'var(--text-muted)',
            fontWeight: 500,
            padding: '4px 4px 8px',
          }}>
            Artifacts ({artifacts.length})
          </div>
          {artifacts.map(art => (
            <ArtifactCard key={art.id} artifact={art} />
          ))}
        </div>
      )}

      {images.length > 0 && (
        <div>
          <div style={{
            fontSize: '11px',
            color: 'var(--text-muted)',
            fontWeight: 500,
            padding: '4px 4px 8px',
          }}>
            Images ({images.length})
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '8px',
          }}>
            {images.map(img => (
              <ImageCard key={img.id} image={img} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
