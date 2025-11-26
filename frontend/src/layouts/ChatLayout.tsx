import { useEffect, useRef, useState } from "react";
import ChatBubble from "../components/ChatBubble";
import { timeNowISO } from "../utils/Time";
import { postChatMessage } from "../api/api";
import { AnimatePresence, motion } from "framer-motion";
import type { Message } from "../types/Message";
import Sidebar from "../components/Sidebar";
import InputChat from "../components/InputChat";

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

      {/* CONTENEDOR GENERAL: CHAT (70%) + SIDEBAR (30%) */}
      <div className="flex flex-1 overflow-hidden">
        {/* CHAT */}
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

        {/* SIDEBAR */}
        <Sidebar />
      </div>
      {/* INPUT, se coloca afuera del sidebar para que se mantenga centrado */}
      <InputChat />
    </div>
  );
}