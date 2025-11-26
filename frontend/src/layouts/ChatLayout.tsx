import { useEffect, useRef, useState } from "react";
import ChatBubble from "../components/ChatBubble";
import { timeNowISO } from "../utils/Time";
import { postChatMessage } from "../api/api";
import { AnimatePresence } from "framer-motion";
import type { Message } from "../types/Message";


interface Props { 
  sessionId: string 
}

export default function ChatLayout({ sessionId }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "system", content: "Hola 👋 Soy tu asistente de teclados mecánicos.", created_at: timeNowISO() }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text: string) {
    if (!text.trim()) return;

    const userMsg: Message = { role: "user", content: text, created_at: timeNowISO() };
    setMessages((s) => [...s, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const data = await postChatMessage(sessionId, text);
      const botMsg: Message = { role: "assistant", content: data.response ?? "Error.", created_at: timeNowISO() };
      setMessages((s) => [...s, botMsg]);
    } catch (err) {
      setMessages((s) => [...s, { role: "assistant", content: "Error de servidor.", created_at: timeNowISO() }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="px-6 py-4 border-b bg-linear-to-r from-indigo-50 to-white">
        <h2 className="text-lg font-semibold">Chat con el Asistente</h2>
        <p className="text-sm text-slate-500">Sesión: <span className="font-mono">{sessionId}</span></p>
      </div>

      <div ref={scrollerRef} className="flex-1 overflow-auto p-6 space-y-3 bg-linear-to-b from-white to-slate-50">
        <AnimatePresence mode="popLayout">
          {messages.map((m, i) => <ChatBubble key={i} m={m} />)}
        </AnimatePresence>
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
        className="p-4 border-t bg-white flex gap-3"
      >
        <input
          className="flex-1 border rounded-md px-3 py-2 focus:ring-2 focus:ring-indigo-200"
          placeholder="Escribe tu mensaje..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button className="bg-indigo-600 text-white px-4 py-2 rounded-md" disabled={loading}>
          {loading ? "Enviando..." : "Enviar"}
        </button>
      </form>
    </div>
  );
}