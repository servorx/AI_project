import { useEffect, useRef, useState } from "react";
import ChatBubble from "../components/ChatBubble";
import { timeNowISO } from "../utils/Time";
import { postChatMessage } from "../api/api";
import { AnimatePresence, motion } from "framer-motion";
import Sidebar from "../components/Sidebar";
import InputChat from "../components/InputChat";
import type { Message } from "../types/Message";
// generar id aleatorio para una sesion de chat web
import { v4 as uuid } from "uuid";

export default function ChatLayout() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hola 👋 Soy tu asistente de teclados mecánicos.",
      created_at: timeNowISO(),
    },
  ]);
  // definir sesionId
  const [sessionId] = useState(uuid());
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const timeout = setTimeout(() => {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 10);
    return () => clearTimeout(timeout);
  }, [messages]);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMsg: Message = {
      role: "user",
      content: input,
      created_at: timeNowISO(),
    };

    setMessages((s) => [...s, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const data = await postChatMessage(sessionId, userMsg.content);

      const botMsg: Message = {
        role: "assistant",
        content: data.response || "Error interno del agente.",
        created_at: timeNowISO(),
      };

      setMessages((s) => [...s, botMsg]);
    } catch (err) {
      console.error("[ERROR]", err);

      setMessages((s) => [
        ...s,
        {
          role: "assistant",
          content:
            "Hubo un error al conectar con el servidor. Intenta nuevamente.",
          created_at: timeNowISO(),
        },
      ]);
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
        className="px-8 py-4 border-b border-border bg-surface"
      >
        <h2 className="text-lg font-semibold text-text-primary">
          Chat con el Asistente
        </h2>
      </motion.div>

      {/* CONTENEDOR GENERAL (Chat + Sidebar) */}
      <div className="flex flex-1 overflow-hidden">
        {/* CHAT */}
        <div
          ref={scrollerRef}
          className="flex-1 overflow-auto px-6 pt-4 pb-1 space-y-4 bg-background"
        >
          <AnimatePresence mode="popLayout">
            {messages.map((m, i) => (
              <ChatBubble key={i} m={m} />
            ))}
          </AnimatePresence>

          <div ref={bottomRef} />
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

      {/* INPUTCHAT COMPONENT */}
      <InputChat
        input={input}
        setInput={setInput}
        loading={loading}
        onSend={sendMessage}
      />
    </div>
  );
}
