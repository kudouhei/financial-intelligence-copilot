import { useReducer } from 'react'

import { runDataQuestion } from '../api'
import type { DataAgentResult } from '../types'

export type DataAgentState =
  | { status: 'idle' }
  | { status: 'loading' }
  | {
      status: 'success'
      result: DataAgentResult
    }
  | {
      status: 'error'
      message: string
    }

type DataAgentAction =
  | { type: 'started' }
  | {
      type: 'succeeded'
      result: DataAgentResult
    }
  | {
      type: 'failed'
      message: string
    }

function reducer(
  _state: DataAgentState,
  action: DataAgentAction,
): DataAgentState {
  switch (action.type) {
    case 'started':
      return { status: 'loading' }

    case 'succeeded':
      return {
        status: 'success',
        result: action.result,
      }

    case 'failed':
      return {
        status: 'error',
        message: action.message,
      }
  }
}

function errorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : 'An unexpected error occurred.'
}

export function useDataAgent() {
  const [state, dispatch] = useReducer(
    reducer,
    { status: 'idle' },
  )

  async function execute(
    question: string,
  ): Promise<void> {
    dispatch({ type: 'started' })

    try {
      const result = await runDataQuestion({
        question,
      })

      dispatch({
        type: 'succeeded',
        result,
      })
    } catch (error) {
      dispatch({
        type: 'failed',
        message: errorMessage(error),
      })
    }
  }

  return {
    state,
    execute,
  }
}