import { ResearchForm } from './components/ResearchForm'
import { ResearchResultPanel } from './components/ResearchResultPanel'
import { useResearch } from './hooks/useResearch'
import './research.css'

export function ResearchWorkspace() {
  const { state, execute } = useResearch()

  return (
    <div className="workspace">
      <ResearchForm
        isSubmitting={state.status === 'loading'}
        onSubmit={execute}
      />

      <ResearchResultPanel state={state} />
    </div>
  )
}