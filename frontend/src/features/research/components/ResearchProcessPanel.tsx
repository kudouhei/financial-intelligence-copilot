import type {ResearchProcess, SourceAction, SourceScreening} from '../types'

type ResearchProcessPanelProps = {
    process: ResearchProcess
}

type MetricProps = {
    label: string
    value: number | null
}

const actionLabels: Record<SourceAction, string> = {
    keep: 'Kept',
    exclude: 'Excluded',
    needs_verification: 'Needs verification',
}

function Metric({ label, value }: MetricProps) {
    return (
      <div className="process-metric">
        <span>{label}</span>
        <strong>{value ?? '—'}</strong>
      </div>
    )
}

function SourceDecisionCard({
    source,
  }: {
    source: SourceScreening
  }) {
    return (
      <li className="surface-card source-decision">
        <div className="source-decision-heading">
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
          >
            {source.title}
          </a>
  
          <span
            className={`source-action source-action--${source.action}`}
          >
            {actionLabels[source.action]}
          </span>
        </div>
  
        <p>{source.reason}</p>
      </li>
    )
}

export function ResearchProcessPanel({
    process,
  }: ResearchProcessPanelProps) {
    const scope = process.scope
  
    return (
      <section
        className="panel process-panel"
        aria-labelledby="research-process-heading"
      >
        <div className="panel-heading">
          <p className="eyebrow">Research process</p>
          <h2 id="research-process-heading">
            How the evidence was selected
          </h2>
        </div>
  
        {scope ? (
          <div className="process-scope">
            <span className="result-label">
              Identified scope
            </span>
  
            <dl className="scope-list">
              <div className="surface-card">
                <dt>Companies</dt>
                <dd>
                  {scope.companies.length > 0
                    ? scope.companies.join(', ')
                    : 'Not specified'}
                </dd>
              </div>
  
              <div className="surface-card">
                <dt>Document types</dt>
                <dd>
                  {scope.document_types.length > 0
                    ? scope.document_types.join(', ')
                    : 'Not specified'}
                </dd>
              </div>
  
              <div className="surface-card">
                <dt>Report years</dt>
                <dd>
                  {scope.report_years.length > 0
                    ? scope.report_years.join(', ')
                    : 'Not specified'}
                </dd>
              </div>
  
              <div className="surface-card">
                <dt>Latest requested</dt>
                <dd>
                  {scope.latest_requested ? 'Yes' : 'No'}
                </dd>
              </div>
            </dl>
  
            <div className="evidence-query">
              <span>Evidence query</span>
              <p>{scope.evidence_query}</p>
            </div>
          </div>
        ) : (
          <p className="process-unavailable">
            Structured scope was not used for this run.
          </p>
        )}
  
        <div
          className="process-metrics"
          aria-label="Research stage counts"
        >
          <Metric
            label="Candidates"
            value={process.candidate_count}
          />
          <Metric
            label="Selected"
            value={process.selected_count}
          />
          <Metric
            label="Extracted"
            value={process.extracted_count}
          />
        </div>
  
        {process.sources.length > 0 && (
          <div>
            <span className="result-label">
              Source screening
            </span>
  
            <ul className="source-decisions">
              {process.sources.map((source) => (
                <SourceDecisionCard
                  key={`${source.source_index}-${source.url}`}
                  source={source}
                />
              ))}
            </ul>
          </div>
        )}
  
        {process.stop_reason && (
          <div className="process-stop" role="status">
            <strong>Research stopped</strong>
            <span>{process.stop_reason}</span>
          </div>
        )}
      </section>
    )
  }