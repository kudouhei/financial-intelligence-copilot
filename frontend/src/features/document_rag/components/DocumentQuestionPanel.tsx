import { useState } from 'react'
import type { SubmitEvent } from 'react'

import { BusyText } from '../../../components/BusyText'

type DocumentQuestionPanelProps = {
  isReady: boolean
  isSubmitting: boolean
  onSubmit: (
    question: string,
    topK: number,
  ) => Promise<void>
}

export function DocumentQuestionPanel({
  isReady,
  isSubmitting,
  onSubmit,
}: DocumentQuestionPanelProps) {
  const [question, setQuestion] = useState(
    'How does the EIB manage liquidity and funding risk?',
  )
  const [topK, setTopK] = useState(10)

  function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    void onSubmit(question, topK)
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">
          02 / Document question
        </p>
        <h2>Ask about the uploaded document</h2>
      </div>

      <form
        className="stack-form"
        onSubmit={handleSubmit}
      >
        <label htmlFor="document-question">
          Question
        </label>

        <textarea
          id="document-question"
          className="form-control"
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          rows={5}
          minLength={3}
          disabled={!isReady || isSubmitting}
          required
        />

        <label htmlFor="document-top-k">
          Evidence chunks
        </label>

        <input
          id="document-top-k"
          className="form-control"
          type="number"
          value={topK}
          min={1}
          max={12}
          disabled={!isReady || isSubmitting}
          onChange={(event) =>
            setTopK(Number(event.target.value))
          }
        />

        {!isReady && (
          <p className="document-guidance">
            Upload and index a PDF to enable questions.
          </p>
        )}

        <button
          className="primary-button"
          type="submit"
          aria-busy={isSubmitting}
          disabled={
            !isReady ||
            isSubmitting ||
            !question.trim()
          }
        >
          <BusyText
            idle="Ask document"
            busy="Retrieving evidence"
            isBusy={isSubmitting}
          />
        </button>
      </form>
    </section>
  )
}