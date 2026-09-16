import { DocumentUploadPanel } from '../document_rag/components/DocumentUploadPanel'
import { CopilotAnswerPanel } from './components/CopilotAnswerPanel'
import { CopilotQuestionPanel } from './components/CopilotQuestionPanel'
import { useCopilot } from './hooks/useCopilot'

import './copilot.css'

export function CopilotWorkspace() {
  const { state, upload, ask } = useCopilot()

  return (
    <div className="workspace-grid">
      <DocumentUploadPanel
        state={state.upload}
        onUpload={upload}
      />

      <div className="workspace-column">
        <CopilotQuestionPanel
          hasDocument={state.upload.status === 'success'}
          isSubmitting={state.answer.status === 'loading'}
          onSubmit={ask}
        />

        <CopilotAnswerPanel state={state.answer} />
      </div>
    </div>
  )
}