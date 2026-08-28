import type {
  ChatMessage,
  ChatMessageAccepted,
  ChatSession,
  FieldDefinition,
  Rule,
} from '../types/rule'

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

function friendlyNetworkError(err: unknown): Error {
  if (err instanceof TypeError) {
    return new Error(
      'Network request failed. Check that Docker services are running (docker compose ps), then retry.',
    )
  }
  if (err instanceof Error) return err
  return new Error('Request failed')
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers ?? {}),
      },
      ...init,
    })
  } catch (err) {
    throw friendlyNetworkError(err)
  }

  if (!response.ok) {
    const text = await response.text()
    if (response.status === 504 || response.status === 502) {
      throw new Error(
        `Gateway error (${response.status}). Wait for containers to become healthy and retry.`,
      )
    }
    throw new Error(text || `Request failed: ${response.status}`)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return response.json() as Promise<T>
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export const api = {
  health: () => request<{ status: string; database: boolean; ollama: boolean }>('/health'),

  listFields: () => request<FieldDefinition[]>('/fields'),
  createField: (body: {
    key: string
    label: string
    data_type: string
    operators: string[]
  }) =>
    request<FieldDefinition>('/fields', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  listRules: () => request<Rule[]>('/rules'),
  getRule: (id: string) => request<Rule>(`/rules/${id}`),
  createRule: (body: Partial<Rule> & { name: string; condition_tree: Rule['condition_tree'] }) =>
    request<Rule>('/rules', { method: 'POST', body: JSON.stringify(body) }),
  updateRule: (id: string, body: Partial<Rule>) =>
    request<Rule>(`/rules/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteRule: (id: string) =>
    request<void>(`/rules/${id}`, { method: 'DELETE' }),

  createChatSession: (ruleId?: string | null) =>
    request<ChatSession>('/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({ rule_id: ruleId ?? null }),
    }),
  listChatMessages: (sessionId: string) =>
    request<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`),
  getChatMessage: (messageId: string) =>
    request<ChatMessage>(`/chat/messages/${messageId}`),

  /** Starts generation asynchronously (HTTP 202). Poll getChatMessage until complete/error. */
  postChatMessage: (sessionId: string, content: string) =>
    request<ChatMessageAccepted>(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),

  async waitForChatMessage(
    messageId: string,
    opts?: { intervalMs?: number; timeoutMs?: number; onTick?: (msg: ChatMessage) => void },
  ): Promise<ChatMessage> {
    const intervalMs = opts?.intervalMs ?? 2000
    const timeoutMs = opts?.timeoutMs ?? 600_000
    const started = Date.now()

    while (Date.now() - started < timeoutMs) {
      const msg = await api.getChatMessage(messageId)
      opts?.onTick?.(msg)
      if (msg.status === 'complete' || msg.status === 'error') {
        return msg
      }
      await sleep(intervalMs)
    }
    throw new Error('Timed out waiting for the model. Try again with a shorter prompt.')
  },
}
