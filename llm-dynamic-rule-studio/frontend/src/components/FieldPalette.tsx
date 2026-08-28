import type { FieldDefinition } from '../types/rule'

interface FieldPaletteProps {
  fields: FieldDefinition[]
}

export function FieldPalette({ fields }: FieldPaletteProps) {
  return (
    <aside className="field-palette">
      <h3>Field catalog</h3>
      <ul>
        {fields.map((f) => (
          <li key={f.key}>
            <strong>{f.label}</strong>
            <span className="muted">
              {f.key} · {f.data_type}
            </span>
          </li>
        ))}
      </ul>
    </aside>
  )
}
