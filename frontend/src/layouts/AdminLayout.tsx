import { useEffect, useState } from "react";
import { getConversations } from "../api/api_conversation";
import { getMessages } from "../api/api_messages";
import { motion } from "framer-motion";
import type { Message } from "../types/Message";
import Skeleton from "../components/admin/Skeleton";
// importar panel de usuarios
import UsersPanel from "../components/admin/UserPanel";

export default function AdminLayout() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  // crud de usuarios 
  const [tab, setTab] = useState<"conversations" | "users">("conversations");

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

      {/* MAIN PANEL */}
      <main className="flex-1 p-0 overflow-auto bg-background">

        {/* selector de pestañas */}
        <div className="flex space-x-4 px-6 py-3 border-b border-border bg-surface">
          <button
            onClick={() => setTab("conversations")}
            className={`font-medium transition ${
              tab === "conversations" ? "text-primary border-b-2 border-primary" : "text-text-secondary"
            }`}
          >
            Conversaciones
          </button>

          <button
            onClick={() => setTab("users")}
            className={`font-medium transition ${
              tab === "users" ? "text-primary border-b-2 border-primary" : "text-text-secondary"
            }`}
          >
            Usuarios
          </button>
        </div>

        {/* PANEL DE CONVERSACIONES */}
        {tab === "conversations" && (
          <div className="p-6">

            <h3 className="font-semibold mb-4 text-text-primary">Mensajes</h3>

            {!selected && (
              <p className="text-text-secondary text-sm">
                Selecciona una conversación
              </p>
            )}

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
                    {m.role} • {(m.created_at ? new Date(m.created_at).toLocaleString() : "—")}
                  </div>

                  <div className="mt-2 whitespace-pre-line text-text-primary">
                    {m.content}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* PANEL DE USUARIOS */}
        {tab === "users" && (
          <UsersPanel />
        )}

      </main>
    </div>
  );
}
