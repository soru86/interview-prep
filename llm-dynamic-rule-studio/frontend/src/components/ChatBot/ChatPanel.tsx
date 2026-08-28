import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../../api/client'
import type { ChatMessage as ChatMessageType, GeneratedRulePayload } from '../../types/rule'
import { ChatMessage } from './ChatMessage'

interface ChatPanelProps {
  ruleId: string | null
  onAddToRule: (payload: GeneratedRulePayload) => void
}

export function ChatPanel({ ruleId, onAddToRule }: ChatPanelProps) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [elapsedSec, setElapsedSec] = useState(0)
  const bottomRef = useRef<HTMLDivElement>(null)
  const initialRuleIdRef = useRef(ruleId)
  const inFlightRef = useRef(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const session = await api.createChatSession(initialRuleIdRef.current)
        if (cancelled) return
        setSessionId(session.id)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to start chat session')
        }
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, elapsedSec])

  useEffect(() => {
    if (!loading) {
      setElapsedSec(0)
      return
    }
    const started = Date.now()
    const id = window.setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - started) / 1000))
    }, 1000)
    return () => window.clearInterval(id)
  }, [loading])

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!sessionId || !input.trim() || loading || inFlightRef.current) return
    const content = input.trim()
    setInput('')
    setLoading(true)
    inFlightRef.current = true
    setError(null)

    try {
      // Short request: persists messages and kicks off background generation.
      const accepted = await api.postChatMessage(sessionId, content)
      setMessages((prev) => [
        ...prev,
        accepted.user_message,
        accepted.assistant_message,
      ])

      const finalMsg = await api.waitForChatMessage(accepted.assistant_message.id, {
        intervalMs: 2000,
        timeoutMs: 600_000,
        onTick: (msg) => {
          setMessages((prev) => prev.map((m) => (m.id === msg.id ? msg : m)))
        },
      })

      setMessages((prev) => prev.map((m) => (m.id === finalMsg.id ? finalMsg : m)))
      if (finalMsg.status === 'error') {
        setError(finalMsg.content)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat request failed')
    } finally {
      setLoading(false)
      inFlightRef.current = false
    }
  }

  return (
    <section className="chat-panel">
      <header className="chat-header">
        <h2>Rule Chatbot</h2>
        <p className="muted">
          Describe a business rule. DeepSeek R1 generates AND/OR fields you can add to the rule
          screen. Generation runs in the background — short network blips won&apos;t kill it.
        </p>
      </header>

      <div className="chat-messages">
        {messages.length === 0 && !loading && (
          <p className="muted chat-empty">
            Try: “VIP customers with cart total over 500 OR loyalty tier gold”
          </p>
        )}
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} onAddToRule={onAddToRule} />
        ))}
        {loading && (
          <p className="muted thinking">
            Working… {elapsedSec}s. You can leave this tab open; polling every 2s until the model
            finishes.
          </p>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <p className="error-text">{error}</p>}

      <form className="chat-input-row" onSubmit={onSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe the business rule…"
          rows={3}
          disabled={loading || !sessionId}
        />
        <button
          type="submit"
          className="primary-btn"
          disabled={loading || !sessionId || !input.trim()}
        >
          Generate
        </button>
      </form>
    </section>
  )
}
