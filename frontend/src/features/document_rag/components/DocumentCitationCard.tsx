import type { DocumentCitation } from '../types'

type DocumentCitationCardProps = {
  citation: DocumentCitation
}

export function DocumentCitationCard({
  citation,
}: DocumentCitationCardProps) {
  return (
    <article className="document-citation">
      <header>
        <strong>PDF page {citation.page_number}</strong>

        <span>
          Similarity{' '}
          {citation.similarity_score.toFixed(3)}
        </span>
      </header>

      <details>
        <summary>View retrieved evidence</summary>
        <p>{citation.excerpt}</p>
      </details>

      <small>{citation.chunk_id}</small>
    </article>
  )
}