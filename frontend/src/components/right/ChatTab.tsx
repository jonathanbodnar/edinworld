import { useState, useRef, useEffect } from 'react'
import { useChapterContext } from '../../context/ChapterContext'
import { useChat } from '../../hooks/useChat'
import AnswerCard from './AnswerCard'
import FormattedText from './FormattedText'

export default function ChatTab() {
  const { activeChapterId, chapterDetail } = useChapterContext()
  const { messages, loading, sendMessage, answerSources, answerContexts, lastAnswer } = useChat(activeChapterId)
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    const query = input.trim()
    setInput('')
    await sendMessage(query)
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    }}>
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid var(--border)',
        fontSize: '12px',
        color: 'var(--text-muted)',
        flexShrink: 0,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span>
          {chapterDetail
            ? `Research Assistant · ${chapterDetail.title}`
            : 'Research Assistant'}
        </span>
        {chapterDetail && (
          <span style={{
            fontSize: '10px',
            padding: '2px 6px',
            borderRadius: '3px',
            background: 'rgba(99, 102, 241, 0.15)',
            color: 'var(--accent)',
          }}>
            chapter focus
          </span>
        )}
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '12px',
      }}>
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '40px 16px',
            color: 'var(--text-muted)',
            fontSize: '13px',
          }}>
            <p>Ask about history, mythology, actors, events, or places.</p>
            <p style={{ marginTop: '8px', fontSize: '11px' }}>
              Answers are grounded in source evidence.
              {chapterDetail && ' Focused on the selected chapter.'}
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={msg.id} style={{ marginBottom: '12px' }}>
            <div style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}>
              <div style={{
                maxWidth: '90%',
                padding: '10px 14px',
                borderRadius: msg.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                background: msg.role === 'user' ? 'var(--accent)' : 'var(--bg-tertiary)',
                color: msg.role === 'user' ? '#fff' : 'var(--text-primary)',
                fontSize: '13px',
                lineHeight: 1.6,
              }}>
                {msg.role === 'assistant'
                  ? <FormattedText text={msg.content} />
                  : msg.content}
              </div>
            </div>

            {msg.role === 'assistant' && msg.answer_packet_id && idx === messages.length - 1 && lastAnswer && (
              <AnswerCard
                answer={lastAnswer}
                sources={answerSources}
                contexts={answerContexts}
              />
            )}
          </div>
        ))}

        {loading && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start',
            marginBottom: '12px',
          }}>
            <div style={{
              padding: '10px 14px',
              borderRadius: '12px 12px 12px 2px',
              background: 'var(--bg-tertiary)',
              color: 'var(--text-muted)',
              fontSize: '13px',
            }}>
              Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} style={{
        padding: '12px',
        borderTop: '1px solid var(--border)',
        display: 'flex',
        gap: '8px',
        flexShrink: 0,
      }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
          style={{
            flex: 1,
            padding: '10px 14px',
            borderRadius: '8px',
            border: '1px solid var(--border)',
            background: 'var(--bg-tertiary)',
            color: 'var(--text-primary)',
            fontSize: '13px',
            outline: 'none',
          }}
          onFocus={e => (e.target.style.borderColor = 'var(--accent)')}
          onBlur={e => (e.target.style.borderColor = 'var(--border)')}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            padding: '10px 16px',
            borderRadius: '8px',
            border: 'none',
            background: loading || !input.trim() ? 'var(--bg-tertiary)' : 'var(--accent)',
            color: loading || !input.trim() ? 'var(--text-muted)' : '#fff',
            fontSize: '13px',
            fontWeight: 600,
            cursor: loading || !input.trim() ? 'default' : 'pointer',
            transition: 'all 0.15s',
          }}
        >
          Send
        </button>
      </form>
    </div>
  )
}
