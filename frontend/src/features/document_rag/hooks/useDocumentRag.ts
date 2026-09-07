import { useReducer } from 'react'

import {
  askDocumentQuestion,
  uploadDocument,
} from '../api'
import type {
  DocumentAnswer,
  DocumentUploadResult,
} from '../types'

type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; message: string }

export type DocumentRagState = {
  upload: AsyncState<DocumentUploadResult>
  answer: AsyncState<DocumentAnswer>
}

type DocumentRagAction =
  | { type: 'upload-started' }
  | {
      type: 'upload-succeeded'
      result: DocumentUploadResult
    }
  | {
      type: 'upload-failed'
      message: string
    }
  | { type: 'question-started' }
  | {
      type: 'question-succeeded'
      result: DocumentAnswer
    }
  | {
      type: 'question-failed'
      message: string
    }

const initialState: DocumentRagState = {
  upload: { status: 'idle' },
  answer: { status: 'idle' },
}

function reducer(
  state: DocumentRagState,
  action: DocumentRagAction,
): DocumentRagState {
  switch (action.type) {
    case 'upload-started':
      return {
        upload: { status: 'loading' },
        answer: { status: 'idle' },
      }

    case 'upload-succeeded':
      return {
        upload: {
          status: 'success',
          data: action.result,
        },
        answer: { status: 'idle' },
      }

    case 'upload-failed':
      return {
        upload: {
          status: 'error',
          message: action.message,
        },
        answer: { status: 'idle' },
      }

    case 'question-started':
      return {
        ...state,
        answer: { status: 'loading' },
      }

    case 'question-succeeded':
      return {
        ...state,
        answer: {
          status: 'success',
          data: action.result,
        },
      }

    case 'question-failed':
      return {
        ...state,
        answer: {
          status: 'error',
          message: action.message,
        },
      }
  }
}

function errorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : 'An unexpected error occurred.'
}

export function useDocumentRag() {
  const [state, dispatch] = useReducer(
    reducer,
    initialState,
  )

  async function upload(file: File): Promise<void> {
    dispatch({ type: 'upload-started' })

    try {
      const result = await uploadDocument(file)

      dispatch({
        type: 'upload-succeeded',
        result,
      })
    } catch (error) {
      dispatch({
        type: 'upload-failed',
        message: errorMessage(error),
      })
    }
  }

  async function ask(
    question: string,
    topK: number,
  ): Promise<void> {
    if (state.upload.status !== 'success') {
      return
    }

    dispatch({ type: 'question-started' })

    try {
      const result = await askDocumentQuestion({
        document_id:
          state.upload.data.document.document_id,
        question,
        top_k: topK,
      })

      dispatch({
        type: 'question-succeeded',
        result,
      })
    } catch (error) {
      dispatch({
        type: 'question-failed',
        message: errorMessage(error),
      })
    }
  }

  return {
    state,
    upload,
    ask,
  }
}