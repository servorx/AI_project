import { useEffect, useRef, useState } from "react";
import ChatBubble from "../components/ChatBubble";
import { timeNowISO } from "../utils/Time";
import { postChatMessage } from "../api/api";
import { AnimatePresence, motion } from "framer-motion";
import type { Message } from "../types/Message";
import Loader from "../components/Loader";

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
          content: "Error de servidor. Intenta de nuevo.",
          created_at: timeNowISO(),
        },
      ]);
      // muestra el error en la consola
      console.error("[ERROR] Error de servidor:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-background text-text-primary">
      {/* HEADER */}
      <motion.div
        initial={{ y: -12, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="px-6 py-4 border-b border-border bg-surface"
      >
        <h2 className="text-lg font-semibold text-text-primary">
          Chat con el Asistente
        </h2>
        <p className="text-sm text-text-secondary">
          Sesión: <span className="font-mono">{sessionId}</span>
        </p>
      </motion.div>

      {/* CHAT SCROLLER ================================= */}
      <div
        ref={scrollerRef}
        className="flex-1 overflow-auto p-6 space-y-4 bg-background"
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
            className="text-secondary text-sm"
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
        className="p-4 border-t border-border bg-surface flex gap-3"
      >
        <input
          className="
            flex-1 
            bg-background 
            border border-border 
            rounded-md px-3 py-2 
            text-text-primary
            placeholder-text-secondary
            focus:ring-2 focus:ring-primary 
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
            bg-primary] 
            text-white 
            px-4 py-2 rounded-md 
            shadow-md disabled:opacity-50
          "
        >
          {loading ? <Loader /> : "Enviar"}
        </motion.button>
      </form>
    </div>
  );
}