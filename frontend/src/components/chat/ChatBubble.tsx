import { motion } from "framer-motion";
import type { Message } from "../types/Message";

export default function ChatBubble({ m }: { m: Message }) {
  const isUser = m.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`
        max-w-2/3 w-fit px-3 py-2 rounded-2xl shadow 
        flex flex-col gap-1 wrap-break-word
        ${isUser 
          ? "bg-primary text-background ml-auto rounded-br-sm" 
          : "bg-surface text-text-primary border border-border rounded-bl-sm"
        }
      `}
    >
      {/* Texto */}
      <div className="whitespace-pre-wrap leading-relaxed text-sm">
        {m.content}
      </div>

      {/* Hora */}
      <div
        className={`
          text-xs self-end 
          ${isUser ? "text-background/80" : "text-text-secondary/80"}
        `}
      >
        {m.created_at ? new Date(m.created_at).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"}) : ""}
      </div>
    </motion.div>
  );
}
