import type {
    ResearchRequest,
    ResearchResult,
  } from './types'
  
  export async function runResearch(
    request: ResearchRequest,
  ): Promise<ResearchResult> {
    const response = await fetch('/api/v1/research', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
  
    if (!response.ok) {
      let message = `Research request failed (${response.status})`
  
      try {
        const body = (await response.json()) as {
          detail?: string
        }
  
        if (body.detail) {
          message = body.detail
        }
      } catch {
        // Keep the status-based fallback message.
      }
  
      throw new Error(message)
    }
  
    return (await response.json()) as ResearchResult
  }