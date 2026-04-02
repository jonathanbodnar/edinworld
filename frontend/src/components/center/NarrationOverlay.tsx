import { useState } from 'react'
import type { NarrationPacket } from '../../api'

export default function NarrationOverlay({ narration }: { narration: NarrationPacket }) {
  const [expanded, setExpanded] = useState(false)

  if (!narration.intro_summary && !narration.core_summary) return null

  return (
    <div style={{
      position: 'absolute',
      top: '16px',
      right: '16px',
      width: '300px',
      background: 'rgba(26, 29, 39, 0.95)',
      border: '1px solid var(--border)',
      borderRadius: '8px',
      overflow: 'hidden',
      pointerEvents: 'auto',
    }}>
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%',
          padding: '10px 14px',
          border: 'none',
          background: 'transparent',
          cursor: 'pointer',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent)' }}>
          Narration
        </span>
        <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
          {expanded ? '▼' : '▶'}
        </span>
      </button>

      {expanded && (
        <div style={{ padding: '0 14px 14px', fontSize: '12px', lineHeight: 1.6 }}>
          {narration.intro_summary && (
            <p style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>
              {narration.intro_summary}
            </p>
          )}
          {narration.core_summary && (
            <p style={{ color: 'var(--text-primary)' }}>
              {narration.core_summary}
            </p>
          )}
          {narration.branch_summary && (
            <p style={{ color: 'var(--text-muted)', marginTop: '8px', fontStyle: 'italic' }}>
              {narration.branch_summary}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
