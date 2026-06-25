import { useState } from "react"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"

const sqlTheme = {
  'code[class*="language-"]': {
    color: "#a8e6c8", fontFamily: '"Space Mono", monospace',
    fontSize: "12px", lineHeight: "1.7", background: "transparent",
  },
  'pre[class*="language-"]': { background: "transparent", margin: 0, padding: 0, overflow: "auto" },
  keyword:    { color: "#e8614a" },
  function:   { color: "#ffd080" },
  string:     { color: "#a8e6c8" },
  number:     { color: "#80d4ff" },
  operator:   { color: "#e8c87a" },
  punctuation:{ color: "#6a9a80" },
  comment:    { color: "#4a7a5a", fontStyle: "italic" },
  "class-name": { color: "#ffd080" },
}

export default function SQLViewer({ sql, retriesUsed }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border-3 border-forest overflow-hidden"
         style={{ boxShadow: "4px 4px 0 #1a3d2b" }}>

      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-3 py-2
                   bg-forest text-mint-light hover:bg-forest-light
                   transition-colors font-mono text-xs"
      >
        <div className="flex items-center gap-2">
          <span className="text-coral font-bold">{"</>"}</span>
          <span>generated SQL</span>
          {retriesUsed > 0 && (
            <span className="bg-coral text-warm px-1.5 py-0.5 text-xs">
              {retriesUsed} {retriesUsed === 1 ? "retry" : "retries"}
            </span>
          )}
        </div>
        <span className="text-mint-dark select-none">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="bg-sqldark px-4 py-3 overflow-x-auto">
          <SyntaxHighlighter
            language="sql"
            style={sqlTheme}
            customStyle={{ margin: 0, padding: 0, background: "transparent" }}
          >
            {sql}
          </SyntaxHighlighter>
        </div>
      )}
    </div>
  )
}
