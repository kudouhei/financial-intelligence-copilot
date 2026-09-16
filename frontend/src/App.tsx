import { useState } from 'react'

import { CopilotWorkspace } from './features/copilot/CopilotWorkspace'
import { DataAgentWorkspace } from './features/data_agent/DataAgentWorkspace'
import { DocumentRagWorkspace } from './features/document_rag/DocumentRagWorkspace'
import { ResearchWorkspace } from './features/research/ResearchWorkspace'

const workspaceCopy = {
  copilot: {
    eyebrow: 'Financial intelligence',
    title: 'Ask across research, documents and data',
    description:
      'Ask one question. The copilot selects the relevant capabilities and returns one evidence-grounded answer.',
  },
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

const workspaceTabs: Array<{
  id: WorkspaceMode
  label: string
}> = [
  { id: 'copilot', label: 'Copilot' },
  { id: 'research', label: 'Research' },
  { id: 'documents', label: 'Documents' },
  { id: 'data', label: 'Data' },
]

function App() {
  const [mode, setMode] =
    useState<WorkspaceMode>('copilot')

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
          {workspaceTabs.map((tab) => (
            <button
              key={tab.id}
              id={`workspace-tab-${tab.id}`}
              type="button"
              role="tab"
              aria-selected={mode === tab.id}
              aria-controls="workspace-panel"
              onClick={() => setMode(tab.id)}
            >
              {tab.label}
            </button>
          ))}
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
          {mode === 'copilot' && <CopilotWorkspace />}

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