import type { Citation } from '../types'

type CitationCardProps = {
  citation: Citation
}

export function CitationCard({
  citation,
}: CitationCardProps) {
  return (
    <article className="citation-card">
      <a
        href={citation.url}
        target="_blank"
        rel="noreferrer"
      >
        {citation.title}
      </a>

      <p>{citation.excerpt}</p>
      <small>{citation.citation_id}</small>
    </article>
  )
}