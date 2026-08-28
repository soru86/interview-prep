interface RuleHeaderProps {
  name: string
  description: string
  status: string
  saveStatus: string
  onNameChange: (name: string) => void
  onDescriptionChange: (description: string) => void
  onStatusChange: (status: string) => void
  onSave: () => void
  onNew: () => void
}

export function RuleHeader({
  name,
  description,
  status,
  saveStatus,
  onNameChange,
  onDescriptionChange,
  onStatusChange,
  onSave,
  onNew,
}: RuleHeaderProps) {
  return (
    <header className="rule-header">
      <div className="rule-header-top">
        <div>
          <p className="eyebrow">Rule Screen</p>
          <input
            className="rule-title-input"
            value={name}
            onChange={(e) => onNameChange(e.target.value)}
            aria-label="Rule name"
          />
        </div>
        <div className="rule-header-actions">
          <select value={status} onChange={(e) => onStatusChange(e.target.value)} aria-label="Status">
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="archived">Archived</option>
          </select>
          <button type="button" className="ghost-btn" onClick={onNew}>
            New
          </button>
          <button type="button" className="primary-btn" onClick={onSave}>
            Save Rule
          </button>
        </div>
      </div>
      <textarea
        className="rule-description"
        value={description}
        onChange={(e) => onDescriptionChange(e.target.value)}
        placeholder="Describe what this business rule does..."
        rows={2}
      />
      <p className="save-status" data-status={saveStatus}>
        {saveStatus === 'saving' && 'Saving…'}
        {saveStatus === 'saved' && 'Saved'}
        {saveStatus === 'error' && 'Save failed'}
        {saveStatus === 'idle' && 'Unsaved changes OK'}
      </p>
    </header>
  )
}
