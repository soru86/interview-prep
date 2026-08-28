import type { ConditionNode, FieldDefinition, Operator } from '../../types/rule'

interface ConditionRowProps {
  node: ConditionNode
  fields: FieldDefinition[]
  onChange: (node: ConditionNode) => void
  onRemove: () => void
}

const ALL_OPERATORS: Operator[] = [
  'eq',
  'neq',
  'gt',
  'gte',
  'lt',
  'lte',
  'contains',
  'in',
  'not_in',
]

export function ConditionRow({ node, fields, onChange, onRemove }: ConditionRowProps) {
  const fieldDef = fields.find((f) => f.key === node.field)
  const operators = (fieldDef?.operators?.length ? fieldDef.operators : ALL_OPERATORS) as Operator[]

  return (
    <div className="condition-row">
      <select
        value={node.field}
        onChange={(e) => onChange({ ...node, field: e.target.value })}
        aria-label="Field"
      >
        {fields.map((f) => (
          <option key={f.key} value={f.key}>
            {f.label}
          </option>
        ))}
        {!fields.some((f) => f.key === node.field) && (
          <option value={node.field}>{node.field}</option>
        )}
      </select>

      <select
        value={node.operator}
        onChange={(e) => onChange({ ...node, operator: e.target.value as Operator })}
        aria-label="Operator"
      >
        {operators.map((op) => (
          <option key={op} value={op}>
            {op}
          </option>
        ))}
      </select>

      <input
        value={String(node.value)}
        onChange={(e) => {
          const raw = e.target.value
          const asNum = Number(raw)
          const value =
            fieldDef?.data_type === 'number' && raw !== '' && !Number.isNaN(asNum)
              ? asNum
              : fieldDef?.data_type === 'boolean'
                ? raw === 'true'
                : raw
          onChange({ ...node, value })
        }}
        aria-label="Value"
        placeholder="Value"
      />

      <button type="button" className="icon-btn danger" onClick={onRemove} aria-label="Remove">
        ×
      </button>
    </div>
  )
}
