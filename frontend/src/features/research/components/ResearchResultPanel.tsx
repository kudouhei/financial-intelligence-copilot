import type { ResearchState } from '../hooks/useResearch'
import { CitationCard } from './CitationCard'

type ResearchResultPanelProps = {
  state: ResearchState
}

export function ResearchResultPanel({
  state,
}: ResearchResultPanelProps) {
  return (
    <section
      className="panel"
      aria-live="polite"
    >
      <div className="panel-heading">
        <p className="eyebrow">Research result</p>
        <h2>Evidence and claims</h2>
      </div>

      {state.status === 'idle' && (
        <div className="empty-state">
          Submit a research question to inspect the
          evidence-backed result.
        </div>
      )}

      {state.status === 'loading' && (
        <div className="empty-state" role="status">
          Planning, searching, and synthesizing…
        </div>
      )}

      {state.status === 'error' && (
        <div className="error-state" role="alert">
          <strong>Research failed</strong>
          <span>{state.message}</span>
        </div>
      )}

      {state.status === 'success' && (
        <div className="research-result">
          <div>
            <span className="result-label">Answer</span>
            <p className="research-answer">
              {state.result.answer}
            </p>
          </div>

          <div>
            <span className="result-label">Claims</span>
            <ul className="research-claims">
              {state.result.claims.map(
                (claim, index) => (
                  <li
                    className="surface-card"
                    key={`${claim.statement}-${index}`}
                  >
                    <p>{claim.statement}</p>
                    <small>
                      Sources:{' '}
                      {claim.citation_ids.join(', ')}
                    </small>
                  </li>
                ),
              )}
            </ul>
          </div>

          <div>
            <span className="result-label">
              Citations
            </span>

            <div className="research-citations">
              {state.result.citations.map(
                (citation) => (
                  <CitationCard
                    key={citation.citation_id}
                    citation={citation}
                  />
                ),
              )}
            </div>
          </div>

          {state.result.warnings.length > 0 && (
            <div className="warning">
              {state.result.warnings.join(' ')}
            </div>
          )}

          <footer className="research-result-footer">
            Trace ID: {state.result.trace_id}
          </footer>
        </div>
      )}
    </section>
  )
}