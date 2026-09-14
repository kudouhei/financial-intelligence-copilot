import { useState } from 'react'

import { DocumentRagWorkspace } from './features/document_rag/DocumentRagWorkspace'
import { ResearchWorkspace } from './features/research/ResearchWorkspace'
import { DataAgentWorkspace } from './features/data_agent/DataAgentWorkspace'

const workspaceCopy = {
  research: {
    eyebrow: 'Research agent',
    title: 'Evidence-first financial research',
    description:
      'Research financial questions with traceable claims, screened sources, and citations.',
  },
  documents: {
    eyebrow: 'Document intelligence',
    title: 'Ask questions across financial documents',
    description:
      'Upload a PDF, retrieve relevant evidence, and generate page-level cited answers.',
  },
  data: {
    eyebrow: 'Data agent',
    title: 'Ask questions across financial metrics',
    description:
      'Generate validated SQL and explore traceable results from structured financial data.',
  },
} as const

type WorkspaceMode = keyof typeof workspaceCopy

function App() {
  const [mode, setMode] =
    useState<WorkspaceMode>('research')

  const activeWorkspace = workspaceCopy[mode]

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="product-brand">
          <span className="product-mark">FI</span>

          <span className="product-name">
            Financial Intelligence Copilot
          </span>
        </div>

        <nav
          className="workspace-switcher"
          aria-label="Copilot workspace"
          role="tablist"
        >
          <button
            id="workspace-tab-research"
            type="button"
            role="tab"
            aria-selected={mode === 'research'}
            aria-controls="workspace-panel"
            onClick={() => setMode('research')}
          >
            Research
          </button>

          <button
            id="workspace-tab-documents"
            type="button"
            role="tab"
            aria-selected={mode === 'documents'}
            aria-controls="workspace-panel"
            onClick={() => setMode('documents')}
          >
            Documents
          </button>

          <button
            id="workspace-tab-data"
            type="button"
            role="tab"
            aria-selected={mode === 'data'}
            aria-controls="workspace-panel"
            onClick={() => setMode('data')}
          >
            Data
          </button>
        </nav>

        <span className="status-badge">
          Development
        </span>
      </header>

      <main>
        <section className="workspace-intro">
          <p className="eyebrow">
            {activeWorkspace.eyebrow}
          </p>

          <h1>{activeWorkspace.title}</h1>

          <p>{activeWorkspace.description}</p>
        </section>

        <div
          id="workspace-panel"
          role="tabpanel"
          aria-labelledby={`workspace-tab-${mode}`}
        >
          {mode === 'research' && <ResearchWorkspace />}

          {mode === 'documents' && (
            <DocumentRagWorkspace />
          )}

          {mode === 'data' && <DataAgentWorkspace />}
        </div>
      </main>
    </div>
  )
}

export default App