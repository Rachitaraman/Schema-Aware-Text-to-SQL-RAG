import { useState } from "react"

const PAGE = 20

export default function ResultTable({ columns, rows }) {
  const [page, setPage] = useState(0)
  const totalPages = Math.ceil(rows.length / PAGE)
  const pageRows   = rows.slice(page * PAGE, page * PAGE + PAGE)

  return (
    <div className="border-3 border-forest overflow-hidden"
         style={{ boxShadow: "4px 4px 0 #1a3d2b" }}>

      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2
                      bg-forest text-mint-light font-mono text-xs">
        <div className="flex items-center gap-2">
          <span className="text-coral">▤</span>
          <span>results</span>
        </div>
        <span className="text-mint-dark">
          {rows.length} row{rows.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto bg-warm">
        <table className="w-full text-xs font-mono border-collapse">
          <thead>
            <tr className="bg-mint-card border-b-3 border-forest">
              {columns.map(col => (
                <th key={col}
                    className="px-3 py-2 text-left text-forest font-bold
                               border-r-2 border-forest border-opacity-20 whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, ri) => (
              <tr key={ri}
                  className={`border-b border-forest border-opacity-10 hover:bg-coral-muted transition-colors
                              ${ri % 2 === 0 ? "bg-warm" : "bg-mint-card"}`}>
                {row.map((cell, ci) => (
                  <td key={ci}
                      className="px-3 py-1.5 text-forest border-r border-forest border-opacity-10
                                 whitespace-nowrap max-w-xs truncate"
                      title={String(cell ?? "")}>
                    {cell === null || cell === undefined
                      ? <span className="opacity-30 italic">null</span>
                      : String(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-3 py-2
                        bg-mint-card border-t-3 border-forest font-mono text-xs">
          <button onClick={() => setPage(p => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="pixel-btn bg-forest text-mint-light px-3 py-1 text-xs">
            ← prev
          </button>
          <span className="text-forest opacity-60">
            {page * PAGE + 1}–{Math.min((page + 1) * PAGE, rows.length)} of {rows.length}
          </span>
          <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                  disabled={page === totalPages - 1}
                  className="pixel-btn bg-forest text-mint-light px-3 py-1 text-xs">
            next →
          </button>
        </div>
      )}
    </div>
  )
}
