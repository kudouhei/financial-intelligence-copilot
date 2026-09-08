import { DocumentAnswerPanel } from './components/DocumentAnswerPanel'
import { DocumentQuestionPanel } from './components/DocumentQuestionPanel'
import { DocumentUploadPanel } from './components/DocumentUploadPanel'
import { useDocumentRag } from './hooks/useDocumentRag'

import './document-rag.css'

export function DocumentRagWorkspace() {
  const { state, upload, ask } = useDocumentRag()

  return (
    <div className="document-workspace">
      <DocumentUploadPanel
        state={state.upload}
        onUpload={upload}
      />

      <div className="document-column">
        <DocumentQuestionPanel
          isReady={state.upload.status === 'success'}
          isSubmitting={
            state.answer.status === 'loading'
          }
          onSubmit={ask}
        />

        <DocumentAnswerPanel state={state.answer} />
      </div>
    </div>
  )
}