import { useState } from 'react'
import type { SubmitEvent } from 'react'

import type { ResearchRequest } from '../types'

type ResearchFormProps = {
  isSubmitting: boolean
  onSubmit: (request: ResearchRequest) => Promise<void>
}

const defaultAsOf = new Date().toISOString().slice(0, 16)

export function ResearchForm({ isSubmitting, onSubmit }: ResearchFormProps) {
    const [question, setQuestion] = useState('What are the main risks facing Company A?')
    const [asOf, setAsOf] = useState(defaultAsOf)
    const [maxSources, setMaxSources] = useState(5)

    function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
        event.preventDefault()
        void onSubmit({ question, as_of: `${asOf}:00Z`, max_sources: maxSources })
    }

    return (
        <form
          className="panel stack-form"
          onSubmit={handleSubmit}
        >
          <div className="panel-heading">
            <p className="eyebrow">Research request</p>
            <h2>Ask a financial question</h2>
          </div>
    
          <label htmlFor="question">Question</label>
          <textarea
            id="question"
            className="form-control"
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            rows={5}
            minLength={3}
            required
          />
    
          <div className="research-form-row">
            <div>
              <label htmlFor="as-of">As of (UTC)</label>
              <input
                id="as-of"
                className="form-control"
                type="datetime-local"
                value={asOf}
                onChange={(event) =>
                  setAsOf(event.target.value)
                }
                required
              />
            </div>
    
            <div>
              <label htmlFor="max-sources">
                Max sources
              </label>
              <input
                id="max-sources"
                className="form-control"
                type="number"
                min={1}
                max={20}
                value={maxSources}
                onChange={(event) =>
                  setMaxSources(Number(event.target.value))
                }
                required
              />
            </div>
          </div>
    
          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting || !question.trim()}
          >
            {isSubmitting
              ? 'Running research…'
              : 'Run research'}
          </button>
        </form>
      )

}


