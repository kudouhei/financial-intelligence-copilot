import { useState } from 'react'

import { DocumentRagWorkspace } from './features/document_rag/DocumentRagWorkspace'
import { ResearchWorkspace } from './features/research/ResearchWorkspace'
import './App.css'

function App() {
  const [mode, setMode] = useState<'documents' | 'research'>('research')

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <span className="product-mark">FI</span>
          <span>Financial Intelligence Copilot</span>
        </div>

        <span className="status-badge">Demo mode</span>
      </header>

      <main>
        <nav
          className="workspace-switcher"
          aria-label="Copilot workspace"
        >
          <button
            type="button"
            aria-pressed={mode === 'research'}
            onClick={() => setMode('research')}
          >
            Research Agent
          </button>

          <button
            type="button"
            aria-pressed={mode === 'documents'}
            onClick={() => setMode('documents')}
          >
            Document RAG
          </button>
        </nav>
        <section className="app-hero">
          <p className="eyebrow">Research Agent</p>
          <h1>Evidence-first financial research</h1>
          <p>
            Turn a financial question into traceable
            claims, citations, and a reproducible
            research result.
          </p>
        </section>

        {mode === 'research' ? (
          <ResearchWorkspace />
        ) : (
          <DocumentRagWorkspace />
        )}
      </main>
    </div>
  )
}

export default App