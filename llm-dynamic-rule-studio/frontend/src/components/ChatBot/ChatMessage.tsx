import type { ChatMessage as ChatMessageType, GeneratedRulePayload } from '../../types/rule'
import { AddToRuleButton } from './AddToRuleButton'
import { GeneratedPreview } from './GeneratedPreview'

interface ChatMessageProps {
  message: ChatMessageType
  onAddToRule: (payload: GeneratedRulePayload) => void
}

export function ChatMessage({ message, onAddToRule }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const isPending = message.status === 'pending'
  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="bubble">
        <p>{message.content}</p>
        {isPending && <p className="muted">Status: generating…</p>}
        {!isUser && message.status === 'complete' && message.generated_payload && (
          <>
            <GeneratedPreview payload={message.generated_payload} />
            <AddToRuleButton payload={message.generated_payload} onAdd={onAddToRule} />
          </>
        )}
      </div>
    </div>
  )
}
