import { useEffect, useState } from 'react'
import type { Epoch } from '../../api'
import { api } from '../../api'
import EpochAccordion from './EpochAccordion'

export default function LeftPanel() {
  const [epochs, setEpochs] = useState<Epoch[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getEpochs()
      .then(setEpochs)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflow: 'hidden',
    }}>
      <div style={{
        padding: '20px 16px 12px',
        borderBottom: '1px solid var(--border)',
        flexShrink: 0,
      }}>
        <h1 style={{
          fontSize: '16px',
          fontWeight: 700,
          color: 'var(--accent)',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
        }}>
          Edinworld
        </h1>
        <p style={{
          fontSize: '11px',
          color: 'var(--text-muted)',
          marginTop: '4px',
        }}>
          Canon Explorer
        </p>
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '8px 0',
      }}>
        {loading ? (
          <div style={{ padding: '20px 16px', color: 'var(--text-muted)', fontSize: '13px' }}>
            Loading epochs...
          </div>
        ) : epochs.length === 0 ? (
          <div style={{ padding: '20px 16px', color: 'var(--text-muted)', fontSize: '13px' }}>
            No epochs found. Run the synthesis pipeline to generate canon data.
          </div>
        ) : (
          epochs.map(epoch => (
            <EpochAccordion key={epoch.id} epoch={epoch} />
          ))
        )}
      </div>
    </div>
  )
}
