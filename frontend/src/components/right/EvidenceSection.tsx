import { useWorldContext } from '../../context/WorldContext'

export default function EvidenceSection() {
  const { epochOverview, activeChapterId, activeCulture, cultureDetail } = useWorldContext()

  if (activeCulture && cultureDetail) {
    return <CultureEvidence />
  }

  if (activeChapterId) {
    return <ChapterEvidence />
  }

  if (epochOverview) {
    return <EpochProvenance />
  }

  return null
}

function EpochProvenance() {
  const { epochOverview } = useWorldContext()
  if (!epochOverview) return null

  const { epoch, cultures, total_sources, total_actors, total_events, total_places } = epochOverview

  return (
    <div style={{ padding: '12px 14px' }}>
      <div style={{
        padding: '12px',
        background: 'linear-gradient(135deg, rgba(212, 168, 83, 0.06), rgba(99, 102, 241, 0.03))',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        marginBottom: '12px',
      }}>
        <div style={{
          fontSize: '10px',
          fontWeight: 600,
          color: 'var(--gold)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          marginBottom: '6px',
        }}>
          How this epoch was constructed
        </div>
        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          This view of <strong style={{ color: 'var(--text-primary)' }}>{epoch.title}</strong> was synthesized
          from {total_sources > 0 ? `${total_sources} primary source${total_sources !== 1 ? 's' : ''}` : 'available sources'}
          {cultures.length > 0 && ` spanning ${cultures.length} culture${cultures.length !== 1 ? 's' : ''}`}.
          {total_actors > 0 && ` ${total_actors} historical figures,`}
          {total_events > 0 && ` ${total_events} events,`}
          {total_places > 0 && ` and ${total_places} locations`}
          {(total_actors > 0 || total_events > 0 || total_places > 0) ? ' have been identified.' : ''}
          {' '}No external theories or interpretations are included — all data derives directly from artifacts, inscriptions, and textual records in our database.
        </p>
      </div>

      {cultures.length > 0 && (
        <div>
          <div style={{
            fontSize: '10px',
            fontWeight: 600,
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            marginBottom: '8px',
          }}>
            Cultures Represented
          </div>
          {cultures.map(c => (
            <div key={c.name} style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '6px 8px',
              borderRadius: '4px',
              marginBottom: '3px',
              background: 'var(--bg-tertiary)',
            }}>
              <span style={{ fontSize: '11px', color: 'var(--text-primary)' }}>{c.name}</span>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                {c.source_count} src · {c.actor_count + c.event_count + c.place_count} entities
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ChapterEvidence() {
  const { sources, contexts, artifacts, images } = useWorldContext()
  const empty = sources.length === 0 && contexts.length === 0 && artifacts.length === 0 && images.length === 0

  if (empty) {
    return (
      <div style={{ padding: '24px 14px', color: 'var(--text-muted)', fontSize: '11px', textAlign: 'center' }}>
        No evidence data linked to this chapter yet.
      </div>
    )
  }

  return (
    <div style={{ padding: '10px 14px' }}>
      {sources.length > 0 && (
        <EvidenceGroup title={`Sources (${sources.length})`}>
          {sources.map(src => (
            <div key={src.id} style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '10px',
              marginBottom: '6px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-primary)', flex: 1 }}>
                  {src.title || 'Untitled'}
                </span>
                <span style={{
                  fontSize: '9px',
                  padding: '1px 5px',
                  borderRadius: '3px',
                  background: 'var(--accent-dim)',
                  color: 'var(--accent)',
                  fontWeight: 600,
                  marginLeft: '6px',
                }}>
                  {(src.relevance_weight * 100).toFixed(0)}%
                </span>
              </div>
              {src.excerpt && (
                <p style={{
                  fontSize: '10px',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.5,
                  marginTop: '4px',
                  fontStyle: 'italic',
                  borderLeft: '2px solid var(--gold)',
                  paddingLeft: '6px',
                }}>
                  {src.excerpt.slice(0, 160)}{src.excerpt.length > 160 ? '...' : ''}
                </p>
              )}
            </div>
          ))}
        </EvidenceGroup>
      )}

      {artifacts.length > 0 && (
        <EvidenceGroup title={`Artifacts (${artifacts.length})`}>
          {artifacts.map(art => (
            <div key={art.id} style={{
              display: 'flex',
              gap: '8px',
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '8px',
              marginBottom: '6px',
            }}>
              {art.image_url && (
                <img src={art.image_url} alt={art.title || ''} style={{
                  width: '48px', height: '48px', objectFit: 'cover', borderRadius: '4px', border: '1px solid var(--border)',
                }} />
              )}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {art.title || 'Untitled'}
                </div>
                {art.description && (
                  <div style={{ fontSize: '10px', color: 'var(--text-secondary)', lineHeight: 1.4, marginTop: '2px' }}>
                    {art.description.slice(0, 100)}
                  </div>
                )}
                <div style={{ fontSize: '9px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {[art.location, art.date_label].filter(Boolean).join(' · ')}
                </div>
              </div>
            </div>
          ))}
        </EvidenceGroup>
      )}

      {images.length > 0 && (
        <EvidenceGroup title={`Images (${images.length})`}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
            {images.map(img => (
              <div key={img.id} style={{
                borderRadius: '6px', overflow: 'hidden', border: '1px solid var(--border)', background: 'var(--bg-tertiary)',
              }}>
                {img.image_url ? (
                  <img src={img.image_url} alt={img.caption || ''} style={{ width: '100%', height: '80px', objectFit: 'cover' }} />
                ) : (
                  <div style={{ width: '100%', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '9px' }}>
                    No image
                  </div>
                )}
                {img.caption && (
                  <div style={{ padding: '4px 6px', fontSize: '9px', color: 'var(--text-secondary)' }}>
                    {img.caption.slice(0, 60)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </EvidenceGroup>
      )}

      {contexts.length > 0 && (
        <EvidenceGroup title={`Contextual Statements (${contexts.length})`}>
          {contexts.slice(0, 10).map(ctx => (
            <div key={ctx.id} style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '8px 10px',
              marginBottom: '4px',
              fontSize: '10px',
              color: 'var(--text-secondary)',
              lineHeight: 1.5,
            }}>
              {ctx.summary || ctx.artifact_description || 'Context reference'}
            </div>
          ))}
        </EvidenceGroup>
      )}
    </div>
  )
}

function CultureEvidence() {
  const { activeCulture, cultureDetail } = useWorldContext()
  if (!cultureDetail || !activeCulture) return null

  return (
    <div style={{ padding: '10px 14px' }}>
      <div style={{
        padding: '10px',
        background: 'linear-gradient(135deg, rgba(212, 168, 83, 0.06), transparent)',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        marginBottom: '10px',
      }}>
        <div style={{ fontSize: '10px', fontWeight: 600, color: 'var(--gold)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>
          {activeCulture} — Source Evidence
        </div>
        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          {cultureDetail.sources.length} source{cultureDetail.sources.length !== 1 ? 's' : ''} from {activeCulture} tradition
          · {cultureDetail.actors.length} actors
          · {cultureDetail.events.length} events
          · {cultureDetail.places.length} places.
          All data from primary artifacts and inscriptions only.
        </p>
      </div>

      {cultureDetail.sources.length > 0 && (
        <EvidenceGroup title={`Sources (${cultureDetail.sources.length})`}>
          {cultureDetail.sources.slice(0, 12).map(src => (
            <div key={src.id} style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '8px 10px',
              marginBottom: '4px',
            }}>
              <div style={{ fontSize: '11px', fontWeight: 500, color: 'var(--text-primary)' }}>
                {src.title || 'Untitled'}
              </div>
              {src.excerpt && (
                <p style={{ fontSize: '10px', color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: '3px', lineHeight: 1.4 }}>
                  {src.excerpt.slice(0, 120)}
                </p>
              )}
            </div>
          ))}
        </EvidenceGroup>
      )}
    </div>
  )
}

function EvidenceGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: '12px' }}>
      <div style={{
        fontSize: '10px',
        fontWeight: 600,
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.06em',
        marginBottom: '6px',
      }}>
        {title}
      </div>
      {children}
    </div>
  )
}
