import type { CopilotSource } from '../types'

type CopilotSourceCardProps = {
  source: CopilotSource
}

export function CopilotSourceCard({
  source,
}: CopilotSourceCardProps) {
  return (
    <article className="surface-card copilot-source-card">
      <header>
        <span className="module-chip">
          {source.module}
        </span>

        {source.page_number !== null && (
          <span>Page {source.page_number}</span>
        )}
      </header>

      {source.url ? (
        <a
          href={source.url}
          target="_blank"
          rel="noreferrer"
        >
          {source.label}
        </a>
      ) : (
        <strong>{source.label}</strong>
      )}

      <details>
        <summary>View supporting evidence</summary>
        <p>{source.excerpt}</p>
      </details>
    </article>
  )
}