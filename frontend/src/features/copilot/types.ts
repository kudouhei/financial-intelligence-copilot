export type CopilotRequest = {
    question: string
    document_id?: string
  }
  
  export type CopilotSource = {
    source_id: string
    module: 'research' | 'document' | 'data'
    label: string
    excerpt: string
    url: string | null
    page_number: number | null
  }
  
  export type CopilotAnswer = {
    question: string
    answer: string
    coverage: 'complete' | 'partial' | 'insufficient'
    sources: CopilotSource[]
    used_modules: Array<'research' | 'document' | 'data'>
    routing_reason: string
    warnings: string[]
    trace_id: string
  }