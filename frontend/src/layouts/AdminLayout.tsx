import { useEffect, useState } from "react";
import { getConversations, getMessages } from "../api/api";
import { motion } from "framer-motion";

export default function AdminLayout() {
  const [conversations, setConversations] = useState<unknown[]>([]);
  const [messages, setMessages] = useState<unknown[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  async function loadConvs() {
    const data = await getConversations();
    setConversations(data.items || []);
  }

  async function loadMsgs(id: number) {
    const data = await getMessages(id);
    setSelected(id);
    setMessages(data.items || []);
  }

  useEffect(() => { loadConvs(); }, []);

  return (
    <div className="flex h-full">
      <aside className="w-80 bg-white border-r p-4 overflow-auto">
        <h3 className="font-semibold mb-2">Conversaciones</h3>
        {conversations.map((c) => (
          <motion.div
            key={c.id}
            whileHover={{ scale: 1.02 }}
            onClick={() => loadMsgs(c.id)}
            className="p-3 rounded-md cursor-pointer hover:bg-slate-50"
          >
            <div>{c.user_phone || c.session_id}</div>
            <div className="text-xs text-slate-400">{new Date(c.created_at).toLocaleString()}</div>
          </motion.div>
        ))}
      </aside>

      <main className="flex-1 p-4 overflow-auto bg-slate-50">
        <h3 className="font-semibold mb-4">Mensajes</h3>
        {!selected && <p className="text-slate-500 text-sm">Selecciona una conversación</p>}
        {messages.map((m) => (
          <div key={m.id} className={`p-3 rounded-md mb-2 ${m.role === "assistant" ? "bg-indigo-50" : "bg-white"}`}>
            <div className="text-xs text-slate-400">{m.role} • {new Date(m.created_at).toLocaleString()}</div>
            <div className="mt-1 whitespace-pre-line">{m.content}</div>
          </div>
        ))}
      </main>
    </div>
  );
}