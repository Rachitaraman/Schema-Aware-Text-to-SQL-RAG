import { useEffect, useRef } from "react"
import MessageBubble from "./MessageBubble.jsx"

function LoadingBubble({ stage }) {
  return (
    <div className="flex items-start gap-3 px-4 py-2 animate-slide-up">
      <div className="w-8 h-8 flex-shrink-0 border-3 border-forest bg-mint-card
                      flex items-center justify-center text-base select-none mt-0.5">
        🌲
      </div>
      <div className="pixel-card-sm bg-warm px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex gap-1">
            {[0, 0.2, 0.4].map((delay, i) => (
              <span
                key={i}
                className="w-2 h-2 bg-forest inline-block"
                style={{ animation: `dotBounce 1.2s ease-in-out ${delay}s infinite` }}
              />
            ))}
          </div>
          <span className="text-xs font-mono text-forest opacity-60">{stage}</span>
        </div>
      </div>
    </div>
  )
}

export default function ChatWindow({ messages, loading, loadingStage }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  return (
    <div className="flex-1 overflow-y-auto py-4 space-y-1">
      {messages.map(msg => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {loading && <LoadingBubble stage={loadingStage} />}
      <div ref={bottomRef} />
    </div>
  )
}


