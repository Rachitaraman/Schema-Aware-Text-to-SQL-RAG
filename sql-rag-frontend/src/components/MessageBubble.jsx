import SQLViewer   from "./SQLViewer.jsx"
import ResultTable  from "./ResultTable.jsx"

function UserBubble({ content }) {
  return (
    <div className="flex justify-end px-4 py-1 animate-slide-up">
      <div className="pixel-card bg-coral text-warm px-4 py-3 max-w-lg">
        <p className="text-sm font-mono leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  )
}

function AssistantBubble({ message }) {
  const { content, sql, columns, rows, retries_used, source_tables, error } = message

  return (
    <div className="flex items-start gap-3 px-4 py-1 animate-slide-up">
      <div className="w-8 h-8 flex-shrink-0 border-3 border-forest bg-mint-card
                      flex items-center justify-center text-base select-none mt-1">
        🌲
      </div>

      <div className="flex flex-col gap-2 max-w-2xl w-full">
        {/* Answer text */}
        <div className={`pixel-card-sm px-4 py-3 ${error ? "bg-red-50 border-red-800" : "bg-warm"}`}>
          {error && <span className="text-xs font-mono text-red-700 block mb-1">✗ error</span>}
          <p className="text-sm font-mono text-forest leading-relaxed whitespace-pre-wrap">
            {content}
          </p>
        </div>

        {/* Source tables badge */}
        {source_tables && source_tables.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {source_tables.map(t => (
              <span key={t}
                className="text-xs font-mono text-forest px-2 py-0.5
                           border border-forest border-opacity-30 bg-mint-card">
                {t}
              </span>
            ))}
          </div>
        )}

        {/* SQL viewer */}
        {sql && <SQLViewer sql={sql} retriesUsed={retries_used} />}

        {/* Result table */}
        {columns && rows && rows.length > 0 && (
          <ResultTable columns={columns} rows={rows} />
        )}

        {columns && rows && rows.length === 0 && (
          <div className="pixel-card-sm bg-mint-light px-4 py-2">
            <span className="text-xs font-mono text-forest opacity-60">query returned 0 rows</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default function MessageBubble({ message }) {
  if (message.role === "user") return <UserBubble content={message.content} />
  return <AssistantBubble message={message} />
}
