import { ResearchForm } from './components/ResearchForm'
import { ResearchResultPanel } from './components/ResearchResultPanel'
import { useResearch } from './hooks/useResearch'
import { ResearchProcessPanel } from './components/ResearchProcessPanel'

import './research.css'

export function ResearchWorkspace() {
  const { state, execute } = useResearch()

  return (
    <div className="workspace">
      <ResearchForm
        isSubmitting={state.status === 'loading'}
        onSubmit={execute}
      />

      <div className="workspace-column">
        <ResearchResultPanel state={state} />

        {state.status === 'success' &&
          state.result.process && (
            <ResearchProcessPanel
              process={state.result.process}
            />
          )}
      </div>
    </div>
  )
}