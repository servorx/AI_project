import { motion } from "framer-motion";
import type { Message } from "../types/Message";

export default function ChatBubble({ m }: { m: Message }) {
  const isUser = m.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      className={`max-w-[80%] p-3 rounded-lg my-1 ${isUser ? "bg-indigo-600 text-white ml-auto" : "bg-slate-100 text-slate-900"}`}
    >
      <div className="whitespace-pre-line">{m.content}</div>
      <div className={`text-[10px] mt-2 ${isUser ? "text-indigo-100" : "text-slate-400"}`}>
        {m.created_at ? new Date(m.created_at).toLocaleTimeString() : ""}
      </div>
    </motion.div>
  );
}