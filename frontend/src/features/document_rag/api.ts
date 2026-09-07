import type {
    DocumentAnswer,
    DocumentQuestion,
    DocumentUploadResult,
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
        `Request failed (${response.status})`
      )
    } catch {
      return `Request failed (${response.status})`
    }
  }
  
  export async function uploadDocument(
    file: File,
  ): Promise<DocumentUploadResult> {
    const formData = new FormData()
    formData.append('file', file)
  
    const response = await fetch('/api/v1/documents', {
      method: 'POST',
      body: formData,
    })
  
    if (!response.ok) {
      throw new Error(await getErrorMessage(response))
    }
  
    return (await response.json()) as DocumentUploadResult
  }
  
  export async function askDocumentQuestion(
    request: DocumentQuestion,
  ): Promise<DocumentAnswer> {
    const response = await fetch(
      '/api/v1/document-questions',
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
  
    return (await response.json()) as DocumentAnswer
  }