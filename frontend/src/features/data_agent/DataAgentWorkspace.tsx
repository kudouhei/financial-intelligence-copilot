import { DataAnswerPanel } from './components/DataAnswerPanel'
import { DataQuestionPanel } from './components/DataQuestionPanel'
import { useDataAgent } from './hooks/useDataAgent'

import './data-agent.css'

export function DataAgentWorkspace() {
  const { state, execute } = useDataAgent()

  return (
    <div className="data-workspace">
      <DataQuestionPanel
        isSubmitting={state.status === 'loading'}
        onSubmit={execute}
      />

      <DataAnswerPanel state={state} />
    </div>
  )
}