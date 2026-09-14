import { useState } from 'react'
import type { SubmitEvent } from 'react'

import type { DocumentRagState } from '../hooks/useDocumentRag'

type DocumentUploadPanelProps = {
  state: DocumentRagState['upload']
  onUpload: (file: File) => Promise<void>
}

export function DocumentUploadPanel({
  state,
  onUpload,
}: DocumentUploadPanelProps) {
  const [file, setFile] = useState<File | null>(null)

  function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (file) {
      void onUpload(file)
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Document ingestion</p>
        <h2>Upload a financial document</h2>
      </div>

      <form
        className="stack-form document-upload-form"
        onSubmit={handleSubmit}
      >
        <label htmlFor="document-file">
          PDF document
        </label>

        <input
          id="document-file"
          className="form-control"
          type="file"
          accept=".pdf,application/pdf"
          onChange={(event) =>
            setFile(event.target.files?.[0] ?? null)
          }
          required
        />

        <button
          className="primary-button"
          type="submit"
          disabled={!file || state.status === 'loading'}
        >
          {state.status === 'loading'
            ? 'Extracting and indexing…'
            : 'Upload and index'}
        </button>
      </form>

      {state.status === 'error' && (
        <div className="error-state" role="alert">
          {state.message}
        </div>
      )}

      {state.status === 'success' && (
        <div className="document-summary">
          <div className="document-summary-heading">
            <strong>{state.data.document.filename}</strong>
      
            <span className="document-cache-status">
              {state.data.cache_hit
                ? 'Previously indexed'
                : 'Upload complete'}
            </span>
          </div>

          <dl>
            <div>
              <dt>Pages</dt>
              <dd>{state.data.document.page_count}</dd>
            </div>

            <div>
              <dt>Chunks</dt>
              <dd>{state.data.chunk_count}</dd>
            </div>
          </dl>

          {state.data.warnings.map((warning) => (
            <p key={warning} className="warning">
              {warning}
            </p>
          ))}
        </div>
      )}
    </section>
  )
}