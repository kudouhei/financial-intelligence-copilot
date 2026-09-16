import { useState } from 'react'
import type { SubmitEvent } from 'react'

import { BusyText } from '../../../components/BusyText'

type CopilotQuestionPanelProps = {
  hasDocument: boolean
  isSubmitting: boolean
  onSubmit: (question: string) => Promise<void>
}

export function CopilotQuestionPanel({
  hasDocument,
  isSubmitting,
  onSubmit,
}: CopilotQuestionPanelProps) {
  const [question, setQuestion] = useState(
    'How does the EIB manage liquidity risk, and what was its 2024 liquidity coverage ratio?',
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
        <p className="eyebrow">Ask Copilot</p>
        <h2>Ask one financial question</h2>
        <p>
          The copilot will select research, document
          evidence and structured data as needed.
        </p>
      </div>

      <form
        className="stack-form"
        onSubmit={handleSubmit}
      >
        <label htmlFor="copilot-question">
          Question
        </label>

        <textarea
          id="copilot-question"
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

        <p className="copilot-context-hint">
          {hasDocument
            ? 'The uploaded PDF is available to the planner.'
            : 'No PDF selected. Research and structured data remain available.'}
        </p>

        <button
          className="primary-button"
          type="submit"
          aria-busy={isSubmitting}
          disabled={isSubmitting || !question.trim()}
        >
          <BusyText
            idle="Ask Copilot"
            busy="Planning and gathering evidence"
            isBusy={isSubmitting}
          />
        </button>
      </form>
    </section>
  )
}