import { useState, useCallback } from "react"
import ChatWindow    from "./components/ChatWindow.jsx"
import InputBar      from "./components/InputBar.jsx"
import SchemaSidebar from "./components/SchemaSidebar.jsx"
import { api }       from "./api/client.js"

const STAGES = [
  "Retrieving schema...",
  "Generating SQL...",
  "Validating query...",
  "Executing...",
  "Synthesizing answer...",
]

const WELCOME = [{
  id: 0,
  role: "assistant",
  content: "Ask anything about your database in plain English — I'll retrieve the right schema, write the SQL, validate it, run it, and explain what I found.",
  sql: null, columns: null, rows: null, retries_used: 0,
  source_tables: [], error: false,
}]

export default function App() {
  const [messages,      setMessages]      = useState(WELCOME)
  const [input,         setInput]         = useState("")
  const [loading,       setLoading]       = useState(false)
  const [loadingStage,  setLoadingStage]  = useState("")
  // Multi-turn: track (question, sql) pairs for context
  const [history,       setHistory]       = useState([])

  // Cycle through loading stage labels while waiting for the API
  const animateStages = useCallback(async () => {
    for (const stage of STAGES) {
      setLoadingStage(stage)
      await new Promise(r => setTimeout(r, 600))
    }
  }, [])

  const sendMessage = useCallback(async (question) => {
    if (!question.trim() || loading) return

    const userMsg = {
      id: Date.now(), role: "user", content: question,
      sql: null, columns: null, rows: null,
      retries_used: 0, source_tables: [], error: false,
    }

    setMessages(prev => [...prev, userMsg])
    setInput("")
    setLoading(true)

    // Animate stage labels in background (doesn't block the real request)
    animateStages()

    try {
      const res  = await api.post("/query", {
        question,
        conversation_history: history.slice(-2),
      })
      const data = res.data

      const assistantMsg = {
        id: Date.now() + 1,
        role: "assistant",
        content:      data.answer,
        sql:          data.sql          ?? null,
        columns:      data.columns      ?? null,
        rows:         data.rows         ?? null,
        retries_used: data.retries_used ?? 0,
        source_tables: data.source_tables ?? [],
        error:        data.error        ?? false,
      }

      setMessages(prev => [...prev, assistantMsg])

      // Add to multi-turn history if query succeeded
      if (!data.error && data.sql) {
        setHistory(prev => [...prev, { question, sql: data.sql }])
      }
    } catch (err) {
      const detail = err.response?.data?.detail
        || "Cannot reach the backend. Make sure it is running on port 8000."
      setMessages(prev => [...prev, {
        id: Date.now() + 1, role: "assistant", content: detail,
        sql: null, columns: null, rows: null,
        retries_used: 0, source_tables: [], error: true,
      }])
    } finally {
      setLoading(false)
      setLoadingStage("")
    }
  }, [loading, history, animateStages])

  const handleTableClick = (tableName) =>
    setInput(`Show me a sample of the ${tableName} table`)

  return (
    <div className="h-screen flex flex-col overflow-hidden pixel-bg">

      {/* ── Header ── */}
      <header className="flex items-center justify-between px-5 py-3
                         bg-mint-bg border-b-3 border-forest flex-shrink-0 z-10">
        <div className="flex items-center gap-3">
          <span className="text-2xl select-none">🌲</span>
          <span className="font-pixel text-forest text-4xl leading-none tracking-wide">
            NLQueryEngine
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="hidden sm:block text-xs font-mono text-forest opacity-50">
            natural language → sql → results
          </span>
          <div className="flex items-center gap-2 pixel-card-sm bg-mint-card px-3 py-1">
            <span className="w-2 h-2 rounded-full bg-coral animate-pulse" />
            <span className="text-xs font-mono text-forest">live</span>
          </div>
        </div>
      </header>

      {/* ── Body ── */}
      <div className="flex flex-1 overflow-hidden">
        <SchemaSidebar onTableClick={handleTableClick} />

        <div className="flex flex-col flex-1 overflow-hidden">
          <ChatWindow
            messages={messages}
            loading={loading}
            loadingStage={loadingStage}
          />
          <InputBar
            value={input}
            onChange={setInput}
            onSend={sendMessage}
            loading={loading}
          />
        </div>
      </div>
    </div>
  )
}
