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
  
  export type ResearchResult = {
    answer: string
    claims: Claim[]
    citations: Citation[]
    as_of: string
    warnings: string[]
    trace_id: string
  }