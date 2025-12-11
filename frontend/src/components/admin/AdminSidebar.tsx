import { motion } from "framer-motion";
import type { ConversationItem } from "../../types/api/ConversationItem";

interface Props {
  tab: "conversations" | "users";
  selected: number | null;
  conversations: ConversationItem[];
  loadMsgs: (id: number) => void;
}

export default function AdminSidebar({
  tab,
  selected,
  conversations,
  loadMsgs,
}: Props) {
  return (
    <aside className="w-80 bg-surface border-r border-border p-4 overflow-auto">
      <h3 className="font-semibold mb-3 text-text-primary">
        {tab === "conversations" ? "Conversaciones" : "Usuarios"}
      </h3>

      {tab === "conversations" && (
        <>
          {conversations.map((c) => {
            const isActive = c.id === selected;

            return (
              <motion.div
                key={c.id}
                whileHover={{ scale: 1.02 }}
                onClick={() => loadMsgs(c.id)}
                transition={{ duration: 0.15 }}
                className={`p-3 rounded-lg cursor-pointer mb-2 shadow-sm ${
                  isActive
                    ? "bg-primary/20 border border-primary"
                    : "bg-surface hover:bg-surface/70 border border-border"
                }`}
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
        </>
      )}

      {tab === "users" && (
        <div className="text-text-secondary text-sm">
          <p className="italic">Selecciona una opción del panel</p>
        </div>
      )}
    </aside>
  );
}
