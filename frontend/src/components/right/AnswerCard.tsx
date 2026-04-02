import type { ChatQueryResult, AnswerSource, AnswerContext } from '../../api'

function modeLabel(mode: string): { text: string; color: string } {
  switch (mode) {
    case 'source': return { text: 'Source-backed', color: 'var(--success)' }
    case 'context': return { text: 'Context-based', color: 'var(--accent)' }
    case 'synthesis': return { text: 'Synthesized', color: 'var(--warning)' }
    default: return { text: 'Unsupported', color: 'var(--error)' }
  }
}

export default function AnswerCard({
  answer, sources, contexts,
}: {
  answer: ChatQueryResult
  sources: AnswerSource[]
  contexts: AnswerContext[]
}) {
  const mode = modeLabel(answer.answer_mode)

  return (
    <div style={{
      marginTop: '8px',
      marginLeft: '4px',
      background: 'var(--bg-primary)',
      border: '1px solid var(--border)',
      borderRadius: '6px',
      padding: '10px 12px',
      fontSize: '11px',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
      }}>
        <span style={{ color: mode.color, fontWeight: 600 }}>
          {mode.text}
        </span>
        <span style={{ color: 'var(--text-muted)' }}>
          {(answer.confidence * 100).toFixed(0)}% confidence
        </span>
      </div>

      {sources.length > 0 && (
        <div style={{ marginBottom: '8px' }}>
          <div style={{
            fontSize: '10px',
            color: 'var(--text-muted)',
            fontWeight: 600,
            marginBottom: '4px',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}>
            Referenced Sources
          </div>
          {sources.map(src => (
            <div key={src.id} style={{
              padding: '4px 8px',
              background: 'var(--bg-secondary)',
              borderRadius: '4px',
              marginBottom: '4px',
              color: 'var(--text-secondary)',
            }}>
              {src.excerpt ? src.excerpt.slice(0, 100) + (src.excerpt.length > 100 ? '...' : '') : 'Source reference'}
              {src.support_type && (
                <span style={{
                  marginLeft: '6px',
                  color: 'var(--accent)',
                  fontSize: '10px',
                }}>
                  [{src.support_type}]
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {contexts.length > 0 && (
        <div>
          <div style={{
            fontSize: '10px',
            color: 'var(--text-muted)',
            fontWeight: 600,
            marginBottom: '4px',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}>
            Referenced Context
          </div>
          {contexts.map(ctx => (
            <div key={ctx.id} style={{
              padding: '4px 8px',
              background: 'var(--bg-secondary)',
              borderRadius: '4px',
              marginBottom: '4px',
              color: 'var(--text-secondary)',
            }}>
              {ctx.summary ? ctx.summary.slice(0, 100) + (ctx.summary.length > 100 ? '...' : '') : 'Context reference'}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
