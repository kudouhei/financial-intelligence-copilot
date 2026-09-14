import type {
    DataAgentResult,
    DataQuestion,
  } from './types'
  
  async function getErrorMessage(
    response: Response,
  ): Promise<string> {
    try {
      const body = (await response.json()) as {
        detail?: string
      }
  
      return (
        body.detail ??
        `Data request failed (${response.status})`
      )
    } catch {
      return `Data request failed (${response.status})`
    }
  }
  
  export async function runDataQuestion(
    request: DataQuestion,
  ): Promise<DataAgentResult> {
    const response = await fetch(
      '/api/v1/data-questions',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      },
    )
  
    if (!response.ok) {
      throw new Error(await getErrorMessage(response))
    }
  
    return (await response.json()) as DataAgentResult
  }