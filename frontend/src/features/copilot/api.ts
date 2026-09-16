import type {
    CopilotAnswer,
    CopilotRequest,
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
        `Copilot request failed (${response.status})`
      )
    } catch {
      return `Copilot request failed (${response.status})`
    }
  }
  
  export async function runCopilot(
    request: CopilotRequest,
  ): Promise<CopilotAnswer> {
    const response = await fetch(
      '/api/v1/copilot/questions',
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
  
    return (await response.json()) as CopilotAnswer
  }