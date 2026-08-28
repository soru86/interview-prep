import type { LogicOp } from '../../types/rule'

interface LogicToggleProps {
  value: LogicOp
  onChange: (logic: LogicOp) => void
}

export function LogicToggle({ value, onChange }: LogicToggleProps) {
  return (
    <div className="logic-toggle" role="group" aria-label="Group logic">
      {(['AND', 'OR'] as LogicOp[]).map((op) => (
        <button
          key={op}
          type="button"
          className={value === op ? 'logic-btn active' : 'logic-btn'}
          onClick={() => onChange(op)}
        >
          {op}
        </button>
      ))}
    </div>
  )
}
