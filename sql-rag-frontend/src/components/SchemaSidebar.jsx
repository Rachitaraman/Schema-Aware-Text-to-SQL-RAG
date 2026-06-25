import { useEffect, useState } from "react"
import { api } from "../api/client.js"

const ICONS = ["🌲", "🌳", "🌿"]

export default function SchemaSidebar({ onTableClick }) {
  const [tables,  setTables]  = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(false)
  const [open,    setOpen]    = useState(true)

  useEffect(() => {
    api.get("/schema-tables")
      .then(r => setTables(r.data.tables || []))
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [])

  return (
    <aside className={`flex-shrink-0 flex flex-col border-r-3 border-forest
                       bg-mint-dark transition-all duration-200
                       ${open ? "w-56" : "w-12"}`}>

      {/* Toggle button */}
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center justify-between px-3 py-3
                   border-b-3 border-forest bg-mint-mid hover:bg-mint-dark
                   transition-colors w-full text-left"
      >
        {open && <span className="font-pixel text-forest text-xl leading-none">TABLES</span>}
        <span className="text-forest font-mono text-sm ml-auto">{open ? "◀" : "▶"}</span>
      </button>

      <div className="flex-1 overflow-y-auto py-2">

        {/* Collapsed state — just icons */}
        {!open && (
          <div className="flex flex-col items-center gap-3 py-4 opacity-40">
            {ICONS.map((ic, i) => <span key={i} className="text-xl select-none">{ic}</span>)}
          </div>
        )}

        {open && loading && (
          <p className="px-3 py-4 text-xs font-mono text-forest opacity-60 animate-pulse">
            loading tables...
          </p>
        )}

        {open && error && (
          <p className="px-3 py-4 text-xs font-mono text-coral">
            ✗ backend offline
          </p>
        )}

        {open && !loading && !error && tables.length === 0 && (
          <p className="px-3 py-4 text-xs font-mono text-forest opacity-60">
            no tables indexed
          </p>
        )}

        {open && !loading && tables.map((t, i) => (
          <button
            key={t}
            onClick={() => onTableClick(t)}
            className="w-full text-left px-3 py-2 text-xs font-mono text-forest
                       hover:bg-mint-light border-b border-forest border-opacity-10
                       flex items-center gap-2 group transition-colors"
            title={`Explore ${t}`}
          >
            <span className="opacity-40 group-hover:opacity-70 select-none">
              {ICONS[i % ICONS.length]}
            </span>
            <span className="truncate group-hover:text-coral transition-colors">{t}</span>
          </button>
        ))}
      </div>

      {open && (
        <div className="border-t-3 border-forest px-3 py-2 bg-mint-mid">
          <p className="text-xs font-mono text-forest opacity-40">click to explore</p>
        </div>
      )}
    </aside>
  )
}
