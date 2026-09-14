import { useState } from 'react'
import type { SubmitEvent } from 'react'

type DataQuestionPanelProps = {
  isSubmitting: boolean
  onSubmit: (question: string) => Promise<void>
}

const exampleQuestions = [
  'What were the EIB liquidity coverage ratio values in 2023 and 2024?',
  'How did EIB outstanding borrowings change between 2023 and 2024?',
]

export function DataQuestionPanel({
  isSubmitting,
  onSubmit,
}: DataQuestionPanelProps) {
  const [question, setQuestion] = useState(
    exampleQuestions[0],
  )

  function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    void onSubmit(question)
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Data question</p>
        <h2>Query financial metrics</h2>
        <p>
          Ask a natural-language question over the
          structured financial database.
        </p>
      </div>

      <form
        className="stack-form"
        onSubmit={handleSubmit}
      >
        <label htmlFor="data-question">Question</label>

        <textarea
          id="data-question"
          className="form-control"
          value={question}
          rows={6}
          minLength={3}
          required
          disabled={isSubmitting}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
        />

        <div className="data-examples">
          <span>Examples</span>

          {exampleQuestions.map((example) => (
            <button
              key={example}
              type="button"
              disabled={isSubmitting}
              onClick={() => setQuestion(example)}
            >
              {example}
            </button>
          ))}
        </div>

        <button
          className="primary-button"
          type="submit"
          disabled={
            isSubmitting || !question.trim()
          }
        >
          {isSubmitting
            ? 'Generating and validating SQL…'
            : 'Ask data'}
        </button>
      </form>
    </section>
  )
}