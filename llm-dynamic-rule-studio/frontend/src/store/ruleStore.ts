import { create } from 'zustand'
import type {
  ConditionTree,
  FieldDefinition,
  GeneratedRulePayload,
  GroupNode,
} from '../types/rule'
import { emptyConditionTree } from '../types/rule'

interface RuleState {
  ruleId: string | null
  name: string
  description: string
  status: string
  conditionTree: ConditionTree
  fields: FieldDefinition[]
  saveStatus: 'idle' | 'saving' | 'saved' | 'error'
  lastError: string | null

  setMeta: (patch: Partial<Pick<RuleState, 'name' | 'description' | 'status'>>) => void
  setConditionTree: (tree: ConditionTree) => void
  setFields: (fields: FieldDefinition[]) => void
  loadRule: (rule: {
    id: string
    name: string
    description: string | null
    status: string
    condition_tree: ConditionTree
  }) => void
  resetRule: () => void
  mergeGeneratedPayload: (payload: GeneratedRulePayload) => void
  setSaveStatus: (status: RuleState['saveStatus'], error?: string | null) => void
}

function ensureGroup(tree: ConditionTree | GroupNode): ConditionTree {
  return {
    type: 'group',
    logic: tree.logic ?? 'AND',
    children: tree.children ?? [],
  }
}

export const useRuleStore = create<RuleState>((set, get) => ({
  ruleId: null,
  name: 'Untitled Rule',
  description: '',
  status: 'draft',
  conditionTree: emptyConditionTree(),
  fields: [],
  saveStatus: 'idle',
  lastError: null,

  setMeta: (patch) => set(patch),
  setConditionTree: (tree) => set({ conditionTree: ensureGroup(tree) }),
  setFields: (fields) => set({ fields }),
  loadRule: (rule) =>
    set({
      ruleId: rule.id,
      name: rule.name,
      description: rule.description ?? '',
      status: rule.status,
      conditionTree: ensureGroup(rule.condition_tree),
      saveStatus: 'idle',
      lastError: null,
    }),
  resetRule: () =>
    set({
      ruleId: null,
      name: 'Untitled Rule',
      description: '',
      status: 'draft',
      conditionTree: emptyConditionTree(),
      saveStatus: 'idle',
      lastError: null,
    }),
  mergeGeneratedPayload: (payload) => {
    const existing = get().fields
    const byKey = new Map(existing.map((f) => [f.key, f]))
    for (const f of payload.fields ?? []) {
      if (!byKey.has(f.key)) {
        byKey.set(f.key, {
          id: `local-${f.key}`,
          key: f.key,
          label: f.label,
          data_type: f.data_type,
          operators: f.operators?.length
            ? f.operators
            : ['eq', 'neq', 'gt', 'gte', 'lt', 'lte'],
          created_at: new Date().toISOString(),
        })
      }
    }
    set({
      name: payload.name || get().name,
      description: payload.description ?? get().description,
      conditionTree: ensureGroup(payload.condition_tree),
      fields: Array.from(byKey.values()),
      saveStatus: 'idle',
    })
  },
  setSaveStatus: (saveStatus, error = null) =>
    set({ saveStatus, lastError: error }),
}))
