export type DataQuestion = {
    question: string
  }
  
  export type SqlDraft = {
    sql: string
    explanation: string
    assumptions: string[]
    cannot_answer: boolean
  }
  
  export type SqlQueryResult = {
    sql: string
    columns: string[]
    rows: Record<string, unknown>[]
    row_count: number
    truncated: boolean
  }
  
  export type DataAgentResult = {
    question: string
    answer: string
    draft: SqlDraft
    query_result: SqlQueryResult | null
    warnings: string[]
  }