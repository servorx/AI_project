import { useEffect, useRef, useState } from "react";
import ChatBubble from "../components/ChatBubble";
import { timeNowISO } from "../utils/Time";
import { postChatMessage } from "../api/api";
import { AnimatePresence, motion } from "framer-motion";
import type { Message } from "../types/Message";

interface Props {
  sessionId: string;
}

export default function ChatLayout({ sessionId }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hola 👋 Soy tu asistente de teclados mecánicos.",
      created_at: timeNowISO(),
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollerRef.current?.scrollTo({
      top: scrollerRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  async function sendMessage(text: string) {
    if (!text.trim()) return;

    const userMsg: Message = {
      role: "user",
      content: text,
      created_at: timeNowISO(),
    };

    setMessages((s) => [...s, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const data = await postChatMessage(sessionId, text);

      const botMsg: Message = {
        role: "assistant",
        content: data.response ?? "Error.",
        created_at: timeNowISO(),
      };

      setMessages((s) => [...s, botMsg]);
    } catch (err) {
      setMessages((s) => [
        ...s,
        {
          role: "assistant",
          content: "Error de servidor.",
          created_at: timeNowISO(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[--color-background] text-[--color-text-primary]">
      {/* HEADER ================================= */}
      <motion.div
        initial={{ y: -12, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="px-6 py-4 border-b border-[--color-border] bg-[--color-surface]"
      >
        <h2 className="text-lg font-semibold text-[--color-text-primary]">
          Chat con el Asistente
        </h2>
        <p className="text-sm text-[--color-text-secondary]">
          Sesión: <span className="font-mono">{sessionId}</span>
        </p>
      </motion.div>

      {/* CHAT SCROLLER ================================= */}
      <div
        ref={scrollerRef}
        className="flex-1 overflow-auto p-6 space-y-4 bg-[--color-background]"
      >
        <AnimatePresence mode="popLayout">
          {messages.map((m, i) => (
            <ChatBubble key={i} m={m} />
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-[--color-secondary] text-sm"
          >
            El asistente está escribiendo…
          </motion.div>
        )}
      </div>

      {/* INPUT AREA ================================= */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage(input);
        }}
        className="p-4 border-t border-[--color-border] bg-[--color-surface] flex gap-3"
      >
        <input
          className="
            flex-1 
            bg-[--color-background] 
            border border-[--color-border] 
            rounded-md px-3 py-2 
            text-[--color-text-primary]
            placeholder-[--color-text-secondary]
            focus:ring-2 focus:ring-[--color-primary] 
            duration-200
          "
          placeholder="Escribe tu mensaje…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />

        <motion.button
          whileTap={{ scale: 0.95 }}
          whileHover={{ scale: 1.03 }}
          disabled={loading}
          className="
            bg-[--color-primary] 
            text-white 
            px-4 py-2 rounded-md 
            shadow-md disabled:opacity-50
          "
        >
          {loading ? "Enviando…" : "Enviar"}
        </motion.button>
      </form>
    </div>
  );
}