import { useEffect, useState } from "react";
import { getConversations } from "../api/api_conversation";
import { getMessages } from "../api/api_messages";
import { motion } from "framer-motion";
import type { ConversationItem } from "../types/api/ConversationItem";
import type { Message } from "../types/Message";
import Skeleton from "../components/Skeleton";

export default function AdminLayout() {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadMsgs(id: number) {
    setLoading(true); // empieza el skeleton
    setSelected(id);
    setMessages([]); // limpiar mensajes mientras llegan

    const data = await getMessages(id);

    setMessages(data.items || []);
    setLoading(false);  // termina el skeleton
  }

  useEffect(() => {
    let active = true;

    const loadConversations = async () => {
      const data = await getConversations();
      if (active) setConversations(data.items || []);
    };

    loadConversations();

    return () => { active = false };
  }, []);

  return (
    <div className="flex h-full bg-background text-text-primary">

      {/* SIDEBAR */}
      <aside className="w-80 bg-surface border-r border-border p-4 overflow-auto">
        <h3 className="font-semibold mb-3 text-text-primary">Conversaciones</h3>

        {conversations.map((c) => {
          const isActive = c.id === selected;

          return (
            <motion.div
              key={c.id}
              whileHover={{ scale: 1.02 }}
              onClick={() => loadMsgs(c.id)}
              transition={{ duration: 0.15 }}
              className={`
                p-3 rounded-lg cursor-pointer mb-2 shadow-sm
                ${isActive ? "bg-primary/20 border border-primary" : "bg-surface hover:bg-surface/70 border border-border"}
              `}
            >
              <div className="font-medium text-text-primary">
                {c.user_phone || c.session_id}
              </div>

              <div className="text-xs text-text-secondary mt-1">
                {new Date(c.created_at).toLocaleString()}
              </div>
            </motion.div>
          );
        })}
      </aside>

      {/* MAIN PANEL */}
      <main className="flex-1 p-6 overflow-auto bg-background">
        <h3 className="font-semibold mb-4 text-text-primary">Mensajes</h3>

        {!selected && (
          <p className="text-text-secondary text-sm">
            Selecciona una conversación
          </p>
        )}
        {/* muestra el skeleton mientras carga */}
        {loading && <Skeleton lines={4} />} 

        {!loading && messages.map((m) => {
          const isAssistant = m.role === "assistant";
          return (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`
                p-4 rounded-xl mb-3 shadow-md border
                ${isAssistant
                  ? "bg-surface border-border"
                  : "bg-primary/20 border-primary"
                }
              `}
            >
              <div className="text-xs text-text-secondary">
                {/* se maneja el caso de que el mensaje no tenga fecha de creacion */}
                {m.role} • {(m.created_at ? new Date(m.created_at).toLocaleString() : "—")}
              </div>

              <div className="mt-2 whitespace-pre-line text-text-primary">
                {m.content}
              </div>
            </motion.div>
          );
        })}
      </main>
    </div>
  );
}
