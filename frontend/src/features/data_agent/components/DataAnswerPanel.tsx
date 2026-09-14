import type { DataAgentState } from '../hooks/useDataAgent'
import { QueryResultTable } from './QueryResultTable'

type DataAnswerPanelProps = {
  state: DataAgentState
}

export function DataAnswerPanel({
  state,
}: DataAnswerPanelProps) {
  if (state.status === 'idle') {
    return (
      <section className="data-panel data-placeholder">
        <p className="eyebrow">Data answer</p>
        <h2>Validated results will appear here</h2>
        <p>
          The copilot will generate SQL, validate it,
          execute it through a read-only connection and
          explain the returned data.
        </p>
      </section>
    )
  }

  return (
    <section
      className="data-panel data-answer-panel"
      aria-live="polite"
    >
      <div className="data-panel-heading">
        <p className="eyebrow">Data answer</p>
        <h2>Grounded database response</h2>
      </div>

      {state.status === 'loading' && (
        <div className="data-loading">
          Inspecting the schema, generating SQL and
          validating the result…
        </div>
      )}

      {state.status === 'error' && (
        <div className="data-error" role="alert">
          {state.message}
        </div>
      )}

      {state.status === 'success' && (
        <div className="data-answer">
          <span
            className={
              state.result.draft.cannot_answer
                ? 'data-status data-status--unavailable'
                : 'data-status data-status--complete'
            }
          >
            {state.result.draft.cannot_answer
              ? 'Data unavailable'
              : 'Query completed'}
          </span>

          <p className="data-answer-text">
            {state.result.answer}
          </p>

          {state.result.warnings.map((warning) => (
            <p key={warning} className="data-warning">
              {warning}
            </p>
          ))}

          {state.result.query_result && (
            <>
              <QueryResultTable
                result={state.result.query_result}
              />

              <details className="sql-details">
                <summary>View generated SQL</summary>
                <pre>
                  <code>
                    {state.result.query_result.sql}
                  </code>
                </pre>
              </details>
            </>
          )}

          {state.result.draft.assumptions.length > 0 && (
            <details className="sql-details">
              <summary>View assumptions</summary>
              <ul>
                {state.result.draft.assumptions.map(
                  (assumption) => (
                    <li key={assumption}>
                      {assumption}
                    </li>
                  ),
                )}
              </ul>
            </details>
          )}
        </div>
      )}
    </section>
  )
}