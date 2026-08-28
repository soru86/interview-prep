import type { GeneratedRulePayload } from '../../types/rule'

interface AddToRuleButtonProps {
  payload: GeneratedRulePayload
  onAdd: (payload: GeneratedRulePayload) => void
}

export function AddToRuleButton({ payload, onAdd }: AddToRuleButtonProps) {
  return (
    <button
      type="button"
      className="primary-btn add-to-rule-btn"
      onClick={() => onAdd(payload)}
    >
      Add to Rule Screen
    </button>
  )
}
