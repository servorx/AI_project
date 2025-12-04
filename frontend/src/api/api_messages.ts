import { api } from "./api";
import type { MessageItem } from "../types/api/MessageItem";

// --- MESSAGE MODERATION ---
export async function getMessages(
  conversationId: number
): Promise<{ items: MessageItem[] }> {
  const res = await api.get("/messages", {
    params: { conversation_id: conversationId },
  });
  return res.data;
}

export async function editMessage(msgId: number, content: string) {
  const res = await api.put(`/messages/${msgId}`, { content });
  return res.data;
}

export async function deleteMessage(msgId: number) {
  const res = await api.delete(`/messages/${msgId}`);
  return res.data;
}
