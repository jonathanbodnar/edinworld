import { useState } from 'react'
import type { Epoch } from '../../api'
import ChapterList from './ChapterList'

function formatYear(y: number | null): string {
  if (y === null) return '?'
  if (y < 0) return `${Math.abs(y)} BCE`
  return `${y} CE`
}

export default function EpochAccordion({ epoch }: { epoch: Epoch }) {
  const [open, setOpen] = useState(false)

  return (
    <div style={{ borderBottom: '1px solid var(--border)' }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          border: 'none',
          background: open ? 'var(--bg-tertiary)' : 'transparent',
          cursor: 'pointer',
          transition: 'background 0.15s',
          textAlign: 'left',
        }}
        onMouseEnter={e => {
          if (!open) (e.currentTarget as HTMLElement).style.background = 'var(--bg-hover)'
        }}
        onMouseLeave={e => {
          if (!open) (e.currentTarget as HTMLElement).style.background = 'transparent'
        }}
      >
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {epoch.title}
          </div>
          <div style={{
            fontSize: '11px',
            color: 'var(--text-muted)',
            marginTop: '2px',
          }}>
            {formatYear(epoch.time_start)} — {formatYear(epoch.time_end)}
            {epoch.chapter_count > 0 && ` · ${epoch.chapter_count} ch.`}
          </div>
        </div>
        <span style={{
          color: 'var(--text-muted)',
          fontSize: '12px',
          marginLeft: '8px',
          transition: 'transform 0.15s',
          transform: open ? 'rotate(90deg)' : 'rotate(0deg)',
        }}>
          ▶
        </span>
      </button>

      {open && <ChapterList epochId={epoch.id} />}
    </div>
  )
}
