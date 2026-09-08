import { DocumentUploadPanel } from './components/DocumentUploadPanel'
import { useDocumentRag } from './hooks/useDocumentRag'

import './document-rag.css'

export function DocumentRagWorkspace() {
  const { state, upload } = useDocumentRag()

  return (
    <div className="document-workspace">
      <DocumentUploadPanel
        state={state.upload}
        onUpload={upload}
      />

      <section className="document-panel document-placeholder">
        <p className="eyebrow">Document question</p>
        <h2>Ask about the uploaded document</h2>
        <p>
          Upload and index a PDF before asking a grounded question.
        </p>
      </section>
    </div>
  )
}