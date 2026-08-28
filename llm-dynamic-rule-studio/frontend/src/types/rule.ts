export type LogicOp = 'AND' | 'OR'

export type Operator =
  | 'eq'
  | 'neq'
  | 'gt'
  | 'gte'
  | 'lt'
  | 'lte'
  | 'contains'
  | 'in'
  | 'not_in'

export interface ConditionNode {
  type: 'condition'
  field: string
  operator: Operator
  value: string | number | boolean
}

export interface GroupNode {
  type: 'group'
  logic: LogicOp
  children: Array<ConditionNode | GroupNode>
}

export type ConditionTree = GroupNode

export interface FieldDefinition {
  id: string
  key: string
  label: string
  data_type: string
  operators: string[]
  created_at: string
}

export interface GeneratedField {
  key: string
  label: string
  data_type: string
  operators: string[]
}

export interface GeneratedRulePayload {
  name: string
  description?: string | null
  fields: GeneratedField[]
  condition_tree: ConditionTree
}

export interface Rule {
  id: string
  name: string
  description: string | null
  status: string
  condition_tree: ConditionTree
  created_at: string
  updated_at: string
}

export interface ChatSession {
  id: string
  rule_id: string | null
  created_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant' | string
  content: string
  status?: 'pending' | 'complete' | 'error' | string
  generated_payload: GeneratedRulePayload | null
  created_at: string
}

export interface ChatMessageAccepted {
  user_message: ChatMessage
  assistant_message: ChatMessage
  poll_url: string
}

export function emptyConditionTree(): ConditionTree {
  return { type: 'group', logic: 'AND', children: [] }
}

export function emptyCondition(field = 'cart_total'): ConditionNode {
  return { type: 'condition', field, operator: 'gt', value: 0 }
}
