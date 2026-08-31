import './App.css'
import { ResearchWorkspace } from './features/research/ResearchWorkspace'

function App() {
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
        <section className="app-hero">
          <p className="eyebrow">Research Agent</p>
          <h1>Evidence-first financial research</h1>
          <p>
            Turn a financial question into traceable
            claims, citations, and a reproducible
            research result.
          </p>
        </section>

        <ResearchWorkspace />
      </main>
    </div>
  )
}

export default App