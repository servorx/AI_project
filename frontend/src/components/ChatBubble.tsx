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
        max-w-4/5 p-3 rounded-2xl my-1 shadow-md backdrop-blur-sm 
        ${isUser 
          ? "bg-primary text-background ml-auto" 
          : "bg-surface text-text-primary border border-border"
        }
      `}
    >
      {/* Texto del mensaje */}
      <div className="whitespace-pre-line leading-relaxed">
        {m.content}
      </div>

      {/* Hora */}
      <div
        className={`
          text-xs mt-2 
          ${isUser ? "text-background/80" : "text-text-secondary"}
        `}
      >
        {m.created_at ? new Date(m.created_at).toLocaleTimeString() : ""}
      </div>
    </motion.div>
  );
}
