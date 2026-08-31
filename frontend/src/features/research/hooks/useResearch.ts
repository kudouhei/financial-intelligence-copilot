import { useReducer } from 'react'
import { runResearch } from '../api'
import type {
  ResearchRequest,
  ResearchResult,
} from '../types'

export type ResearchState =
  | { status: 'idle' }
  | { status: 'loading' }
  | {
      status: 'success'
      result: ResearchResult
    }
  | {
      status: 'error'
      message: string
    }

type ResearchAction =
  | { type: 'started' }
  | {
      type: 'succeeded'
      result: ResearchResult
    }
  | {
      type: 'failed'
      message: string
    }


    function researchReducer(
        _state: ResearchState,
        action: ResearchAction,
      ): ResearchState {
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

export function useResearch() {
    const [state, dispatch] = useReducer(researchReducer, { status: 'idle' })

    async function execute(request: ResearchRequest): Promise<void> {
        dispatch({ type: 'started' })

        try {
            const result = await runResearch(request)
      
            dispatch({
              type: 'succeeded',
              result,
            })
          } catch (error) {
            dispatch({
              type: 'failed',
              message:
                error instanceof Error
                  ? error.message
                  : 'An unexpected error occurred.',
            })
          }
    }
    return {state, execute,}
}