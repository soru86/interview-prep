import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { FieldPalette } from '../components/FieldPalette'
import { ChatPanel } from '../components/ChatBot/ChatPanel'
import { ConditionGroup } from '../components/RuleEditor/ConditionGroup'
import { RuleHeader } from '../components/RuleEditor/RuleHeader'
import { useRuleStore } from '../store/ruleStore'
import type { GeneratedRulePayload, Rule } from '../types/rule'

export function RuleStudioPage() {
  const {
    ruleId,
    name,
    description,
    status,
    conditionTree,
    fields,
    saveStatus,
    setMeta,
    setConditionTree,
    setFields,
    loadRule,
    resetRule,
    mergeGeneratedPayload,
    setSaveStatus,
  } = useRuleStore()

  const [rules, setRules] = useState<Rule[]>([])
  const [health, setHealth] = useState<string>('checking…')
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      try {
        const [fieldList, ruleList, h] = await Promise.all([
          api.listFields(),
          api.listRules(),
          api.health(),
        ])
        setFields(fieldList)
        setRules(ruleList)
        setHealth(
          h.status === 'ok'
            ? 'API · DB · Ollama ready'
            : `Degraded (db=${h.database}, ollama=${h.ollama})`,
        )
        if (ruleList[0]) {
          loadRule(ruleList[0])
        }
      } catch (err) {
        setHealth(err instanceof Error ? err.message : 'API unavailable')
      }
    })()
  }, [loadRule, setFields])

  const saveRule = async () => {
    setSaveStatus('saving')
    try {
      const body = {
        name,
        description: description || null,
        status,
        condition_tree: conditionTree,
      }
      let saved: Rule
      if (ruleId) {
        saved = await api.updateRule(ruleId, body)
      } else {
        saved = await api.createRule(body)
      }
      loadRule(saved)
      setSaveStatus('saved')
      const ruleList = await api.listRules()
      setRules(ruleList)
      setToast('Rule saved')
    } catch (err) {
      setSaveStatus('error', err instanceof Error ? err.message : 'Save failed')
    }
  }

  const onAddToRule = (payload: GeneratedRulePayload) => {
    mergeGeneratedPayload(payload)
    setToast(`Added “${payload.name}” to the rule screen`)
    // Persist newly proposed fields to catalog when possible
    ;(async () => {
      for (const f of payload.fields ?? []) {
        if (fields.some((existing) => existing.key === f.key)) continue
        if (f.key.startsWith('local-')) continue
        try {
          await api.createField({
            key: f.key,
            label: f.label,
            data_type: f.data_type,
            operators: f.operators?.length ? f.operators : ['eq', 'neq'],
          })
        } catch {
          // ignore conflicts
        }
      }
      try {
        const refreshed = await api.listFields()
        setFields(refreshed)
      } catch {
        // ignore
      }
    })()
  }

  return (
    <div className="studio-shell">
      <div className="studio-topbar">
        <div>
          <h1 className="brand">LLM Dynamic Rule Studio</h1>
          <p className="muted">{health}</p>
        </div>
        <div className="rule-picker">
          <label>
            Load rule
            <select
              value={ruleId ?? ''}
              onChange={(e) => {
                const id = e.target.value
                if (!id) {
                  resetRule()
                  return
                }
                const found = rules.find((r) => r.id === id)
                if (found) loadRule(found)
              }}
            >
              <option value="">New unsaved rule</option>
              {rules.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="studio-grid">
        <main className="rule-screen">
          <RuleHeader
            name={name}
            description={description}
            status={status}
            saveStatus={saveStatus}
            onNameChange={(n) => setMeta({ name: n })}
            onDescriptionChange={(d) => setMeta({ description: d })}
            onStatusChange={(s) => setMeta({ status: s })}
            onSave={saveRule}
            onNew={resetRule}
          />
          <div className="rule-body">
            <div className="rule-editor-pane">
              <h3>Conditions (AND / OR)</h3>
              <ConditionGroup
                node={conditionTree}
                fields={fields}
                onChange={setConditionTree}
              />
            </div>
            <FieldPalette fields={fields} />
          </div>
        </main>

        <ChatPanel ruleId={ruleId} onAddToRule={onAddToRule} />
      </div>

      {toast && (
        <div className="toast" role="status">
          {toast}
          <button type="button" onClick={() => setToast(null)}>
            Dismiss
          </button>
        </div>
      )}
    </div>
  )
}
