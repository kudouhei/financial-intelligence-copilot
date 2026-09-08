export type DocumentRecord = {
    document_id: string
    filename: string
    media_type: 'application/pdf'
    sha256: string
    page_count: number
    ingested_at: string
  }
  
  export type DocumentUploadResult = {
    document: DocumentRecord
    chunk_count: number
    warnings: string[]
    cache_hit: boolean
  }

  export type DocumentQuestion = {
    document_id: string
    question: string
    top_k: number
  }
  
  export type DocumentCitation = {
    chunk_id: string
    document_id: string
    page_number: number
    excerpt: string
    similarity_score: number
  }
  
  export type DocumentAnswer = {
    document_id: string
    question: string
    answer: string
    citations: DocumentCitation[]
    insufficient_evidence: boolean
    warnings: string[]
  }