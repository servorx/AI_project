import { api } from "./api";
import type { ConversationItem } from "../types/api/ConversationItem";

// metodo api para obtener conversaciones
export async function getConversations(): Promise<{ items: ConversationItem[] }> {
  const res = await api.get("/admin/conversations");
  return res.data;
}

