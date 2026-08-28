import type { ConditionNode, ConditionTree, FieldDefinition, GroupNode, LogicOp } from '../../types/rule'
import { emptyCondition } from '../../types/rule'
import { ConditionRow } from './ConditionRow'
import { LogicToggle } from './LogicToggle'

interface ConditionGroupProps {
  node: GroupNode
  fields: FieldDefinition[]
  depth?: number
  onChange: (node: GroupNode) => void
  onRemove?: () => void
}

function updateChild(
  children: GroupNode['children'],
  index: number,
  next: ConditionNode | GroupNode,
): GroupNode['children'] {
  return children.map((c, i) => (i === index ? next : c))
}

export function ConditionGroup({
  node,
  fields,
  depth = 0,
  onChange,
  onRemove,
}: ConditionGroupProps) {
  const setLogic = (logic: LogicOp) => onChange({ ...node, logic })

  const addCondition = () => {
    const field = fields[0]?.key ?? 'cart_total'
    onChange({ ...node, children: [...node.children, emptyCondition(field)] })
  }

  const addGroup = () => {
    const group: ConditionTree = { type: 'group', logic: 'OR', children: [] }
    onChange({ ...node, children: [...node.children, group] })
  }

  return (
    <div className={`condition-group depth-${Math.min(depth, 3)}`}>
      <div className="group-header">
        <LogicToggle value={node.logic} onChange={setLogic} />
        <div className="group-actions">
          <button type="button" className="ghost-btn" onClick={addCondition}>
            + Condition
          </button>
          <button type="button" className="ghost-btn" onClick={addGroup}>
            + Group
          </button>
          {onRemove && (
            <button type="button" className="ghost-btn danger" onClick={onRemove}>
              Remove group
            </button>
          )}
        </div>
      </div>

      <div className="group-children">
        {node.children.length === 0 && (
          <p className="muted">No conditions yet. Add one or generate from the chatbot.</p>
        )}
        {node.children.map((child, index) => {
          if (child.type === 'condition') {
            return (
              <ConditionRow
                key={`c-${index}`}
                node={child}
                fields={fields}
                onChange={(next) =>
                  onChange({ ...node, children: updateChild(node.children, index, next) })
                }
                onRemove={() =>
                  onChange({
                    ...node,
                    children: node.children.filter((_, i) => i !== index),
                  })
                }
              />
            )
          }
          return (
            <ConditionGroup
              key={`g-${index}`}
              node={child}
              fields={fields}
              depth={depth + 1}
              onChange={(next) =>
                onChange({ ...node, children: updateChild(node.children, index, next) })
              }
              onRemove={() =>
                onChange({
                  ...node,
                  children: node.children.filter((_, i) => i !== index),
                })
              }
            />
          )
        })}
      </div>
    </div>
  )
}
