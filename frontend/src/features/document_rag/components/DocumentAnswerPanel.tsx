import type { DocumentRagState } from '../hooks/useDocumentRag'
import { DocumentCitationCard } from './DocumentCitationCard'

type DocumentAnswerPanelProps = {
  state: DocumentRagState['answer']
}

export function DocumentAnswerPanel({
  state,
}: DocumentAnswerPanelProps) {
  if (state.status === 'idle') {
    return null
  }

  return (
    <section
      className="panel"
      aria-live="polite"
    >
      <div className="panel-heading">
        <p className="eyebrow">Document answer</p>
        <h2>Grounded response</h2>
      </div>

      {state.status === 'loading' && (
        <div className="muted-state">
          Retrieving evidence and generating an answer…
        </div>
      )}

      {state.status === 'error' && (
        <div className="error-state" role="alert">
          {state.message}
        </div>
      )}

      {state.status === 'success' && (
        <div className="document-answer">
          <span
            className={
              state.data.insufficient_evidence
                ? 'status-chip status-chip--warning'
                : 'status-chip status-chip--success'
            }
          >
            {state.data.insufficient_evidence
              ? 'Insufficient evidence'
              : 'Evidence supported'}
          </span>

          <p className="document-answer-text">
            {state.data.answer}
          </p>

          {state.data.citations.length > 0 && (
            <div>
              <h3>Retrieved evidence</h3>

              <div className="document-citations">
                {state.data.citations.map(
                  (citation) => (
                    <DocumentCitationCard
                      key={citation.chunk_id}
                      citation={citation}
                    />
                  ),
                )}
              </div>
            </div>
          )}

          {state.data.warnings.map((warning) => (
            <p key={warning} className="warning">
              {warning}
            </p>
          ))}
        </div>
      )}
    </section>
  )
}