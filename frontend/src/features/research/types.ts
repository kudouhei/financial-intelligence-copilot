export type ResearchRequest = {
  question: string
  as_of: string
  max_sources: number
}

export type Citation = {
  citation_id: string
  title: string
  url: string
  published_at: string | null
  retrieved_at: string
  excerpt: string
}

export type Claim = {
  statement: string
  citation_ids: string[]
}

export type DocumentType =
  | 'annual_report'
  | 'quarterly_report'
  | 'current_report'
  | 'earnings_release'

export type ResearchScope = {
  companies: string[]
  document_types: DocumentType[]
  report_years: number[]
  latest_requested: boolean
  evidence_query: string
}

export type SourceAction =
  | 'keep'
  | 'exclude'
  | 'needs_verification'

export type SourceScreening = {
  source_index: number
  action: SourceAction
  reason: string
  title: string
  url: string
}

export type ResearchProcess = {
  scope: ResearchScope | null
  candidate_count: number | null
  selected_count: number | null
  extracted_count: number | null
  sources: SourceScreening[]
  stop_reason: string | null
}

export type ResearchResult = {
  answer: string
  claims: Claim[]
  citations: Citation[]
  as_of: string
  warnings: string[]
  trace_id: string
  process: ResearchProcess | null
}