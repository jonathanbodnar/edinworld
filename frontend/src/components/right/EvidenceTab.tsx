import { useChapterContext } from '../../context/ChapterContext'
import SourceCard from './SourceCard'

export default function EvidenceTab() {
  const { sources } = useChapterContext()

  if (sources.length === 0) {
    return (
      <div style={{
        padding: '24px 16px',
        color: 'var(--text-muted)',
        fontSize: '13px',
        textAlign: 'center',
      }}>
        No source evidence found for this chapter. Run the evidence bundle builder to populate source links.
      </div>
    )
  }

  return (
    <div style={{ padding: '12px' }}>
      <div style={{
        fontSize: '11px',
        color: 'var(--text-muted)',
        padding: '4px 4px 12px',
        fontWeight: 500,
      }}>
        {sources.length} source{sources.length !== 1 && 's'} linked
      </div>
      {sources.map(source => (
        <SourceCard key={source.id} source={source} />
      ))}
    </div>
  )
}
