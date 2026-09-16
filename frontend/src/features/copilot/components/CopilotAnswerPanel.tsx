import type { CopilotState } from '../hooks/useCopilot'
import { CopilotSourceCard } from './CopilotSourceCard'

type CopilotAnswerPanelProps = {
  state: CopilotState['answer']
}

const coverageLabel = {
  complete: 'Complete answer',
  partial: 'Partial answer',
  insufficient: 'Insufficient evidence',
} as const

export function CopilotAnswerPanel({
  state,
}: CopilotAnswerPanelProps) {
  if (state.status === 'idle') {
    return (
      <section className="panel panel--placeholder">
        <p className="eyebrow">Copilot answer</p>
        <h2>One grounded response will appear here</h2>
        <p>
          The planner will run only the capabilities needed
          for your question.
        </p>
      </section>
    )
  }

  return (
    <section
      className="panel copilot-answer-panel"
      aria-live="polite"
    >
      <div className="panel-heading">
        <p className="eyebrow">Copilot answer</p>
        <h2>Evidence-grounded response</h2>
      </div>

      {state.status === 'loading' && (
        <div className="muted-state">
          Planning, retrieving evidence and synthesizing
          one answer…
        </div>
      )}

      {state.status === 'error' && (
        <div className="error-state" role="alert">
          {state.message}
        </div>
      )}

      {state.status === 'success' && (
        <div className="copilot-answer">
          <span
            className={
              state.data.coverage === 'complete'
                ? 'status-chip status-chip--success'
                : 'status-chip status-chip--warning'
            }
          >
            {coverageLabel[state.data.coverage]}
          </span>

          <p className="copilot-answer-text">
            {state.data.answer}
          </p>

          <div>
            <h3>Modules run</h3>

            <div className="module-list">
              {state.data.used_modules.length > 0 ? (
                state.data.used_modules.map((module) => (
                  <span
                    key={module}
                    className="module-chip"
                  >
                    {module}
                  </span>
                ))
              ) : (
                <span className="copilot-context-hint">
                  No module was executed.
                </span>
              )}
            </div>
          </div>

          {state.data.sources.length > 0 && (
            <div>
              <h3>Supporting evidence</h3>

              <div className="copilot-sources">
                {state.data.sources.map((source) => (
                  <CopilotSourceCard
                    key={source.source_id}
                    source={source}
                  />
                ))}
              </div>
            </div>
          )}

          {state.data.warnings.map((warning) => (
            <p key={warning} className="warning">
              {warning}
            </p>
          ))}

          <details className="copilot-routing-details">
            <summary>Why these modules were selected</summary>
            <p>{state.data.routing_reason}</p>
          </details>

          <small className="trace-id">
            Trace ID: {state.data.trace_id}
          </small>
        </div>
      )}
    </section>
  )
}