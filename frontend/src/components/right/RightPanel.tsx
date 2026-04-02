import { useState } from 'react'
import { useChapterContext } from '../../context/ChapterContext'
import EvidenceTab from './EvidenceTab'
import ContextTab from './ContextTab'
import ChatTab from './ChatTab'

type Tab = 'evidence' | 'context' | 'chat'

export default function RightPanel() {
  const [activeTab, setActiveTab] = useState<Tab>('evidence')
  const { activeChapterId } = useChapterContext()

  const tabs: { id: Tab; label: string }[] = [
    { id: 'evidence', label: 'Evidence' },
    { id: 'context', label: 'Context' },
    { id: 'chat', label: 'Chat' },
  ]

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      borderLeft: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflow: 'hidden',
    }}>
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border)',
        flexShrink: 0,
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: 1,
              padding: '12px 8px',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: activeTab === tab.id ? 600 : 400,
              color: activeTab === tab.id ? 'var(--accent)' : 'var(--text-muted)',
              borderBottom: activeTab === tab.id ? '2px solid var(--accent)' : '2px solid transparent',
              transition: 'all 0.15s',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {!activeChapterId ? (
          <div style={{
            padding: '40px 20px',
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: '13px',
          }}>
            Select a chapter to view evidence, context, and interact with the research assistant.
          </div>
        ) : (
          <>
            {activeTab === 'evidence' && <EvidenceTab />}
            {activeTab === 'context' && <ContextTab />}
            {activeTab === 'chat' && <ChatTab />}
          </>
        )}
      </div>
    </div>
  )
}
