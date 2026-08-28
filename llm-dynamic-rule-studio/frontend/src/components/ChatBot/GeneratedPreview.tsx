import type { GeneratedRulePayload, GroupNode } from '../../types/rule'

interface GeneratedPreviewProps {
  payload: GeneratedRulePayload
}

function summarizeNode(node: GroupNode | GeneratedRulePayload['condition_tree'], depth = 0): string[] {
  const lines: string[] = []
  const indent = '  '.repeat(depth)
  lines.push(`${indent}(${node.logic})`)
  for (const child of node.children) {
    if (child.type === 'condition') {
      lines.push(`${indent}  ${child.field} ${child.operator} ${JSON.stringify(child.value)}`)
    } else {
      lines.push(...summarizeNode(child, depth + 1))
    }
  }
  return lines
}

export function GeneratedPreview({ payload }: GeneratedPreviewProps) {
  return (
    <div className="generated-preview">
      <h4>{payload.name}</h4>
      {payload.description && <p className="muted">{payload.description}</p>}
      {payload.fields?.length > 0 && (
        <p className="preview-fields">
          Fields: {payload.fields.map((f) => f.key).join(', ')}
        </p>
      )}
      <pre>{summarizeNode(payload.condition_tree).join('\n')}</pre>
    </div>
  )
}
