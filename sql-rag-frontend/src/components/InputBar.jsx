import { useRef } from "react"

const EXAMPLES = [
  "Top 5 customers by total spend",
  "Monthly sales trend for 2009",
  "Which artist has the most albums?",
  "Revenue by country",
]

export default function InputBar({ value, onChange, onSend, loading }) {
  const ref = useRef(null)

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      onSend(value)
    }
  }

  return (
    <div className="flex-shrink-0 border-t-3 border-forest bg-mint-bg px-4 py-3">

      {/* Example chips — only visible when input is empty and not loading */}
      {!value && !loading && (
        <div className="flex flex-wrap gap-2 mb-2">
          {EXAMPLES.map(ex => (
            <button
              key={ex}
              onClick={() => { onChange(ex); ref.current?.focus() }}
              className="text-xs font-mono text-forest px-2 py-1
                         border-2 border-forest border-opacity-40 bg-mint-card
                         hover:bg-coral hover:text-warm hover:border-coral transition-colors"
            >
              {ex}
            </button>
          ))}
        </div>
      )}

      {/* Input row */}
      <div className="flex gap-3 items-end">
        <div className="flex-1 pixel-card bg-warm">
          <textarea
            ref={ref}
            value={value}
            onChange={e => onChange(e.target.value)}
            onKeyDown={handleKey}
            disabled={loading}
            rows={2}
            placeholder="Ask anything about your database... (Enter to send)"
            className="w-full bg-transparent text-sm font-mono text-forest
                       px-3 py-2 resize-none outline-none
                       placeholder:text-forest placeholder:opacity-30
                       disabled:opacity-50"
          />
        </div>

        <button
          onClick={() => onSend(value)}
          disabled={loading || !value.trim()}
          className="pixel-btn bg-coral text-warm font-mono font-bold text-sm
                     px-5 py-3 flex-shrink-0 flex items-center gap-2"
        >
          {loading
            ? <><span className="w-2 h-2 bg-warm rounded-full animate-pulse" /> wait</>
            : <>run <span className="text-lg leading-none">→</span></>
          }
        </button>
      </div>

      <p className="text-xs font-mono text-forest opacity-30 mt-1.5">
        Enter ↵ to send · Shift+Enter for newline · results capped at 100 rows
      </p>
    </div>
  )
}
