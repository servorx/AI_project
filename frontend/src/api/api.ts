import axios from "axios";
// importar los types 
import type { ConversationItem } from "./types/Conversation";

export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// crear la constante de axios
export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Logs de request
api.interceptors.request.use(
  (config) => {
    console.log("[API REQUEST]", config.method, config.url);
    return config;
  },
  (error) => {
    console.error("[API REQUEST ERROR]", error);
    return Promise.reject(error);
  }
);

// Logs de response
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("[API RESPONSE ERROR]", error);
    return Promise.reject(error);
  }
);

// estas son las interfaces de los tipos de datos que se esperan de la API
export interface ChatResponse {
  response: string;
}

export interface ConversationItem {
  id: number;
  created_at: string;
  session_id?: string;
  user_phone?: string;
}

export interface MessageItem {
  id: number;
  conversation_id: number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

// estas son las funciones de la API
export async function postChatMessage(
  sessionId: string,
  message: string
): Promise<ChatResponse> {
  const resp = await api.post("/chat/", {
    params: { session_id: sessionId },
    data: { message },
  });
  return resp.data;
}

export async function getConversations(): Promise<{ items: ConversationItem[] }> {
  const res = await api.get("/admin/conversations");
  return res.data;
}

export async function getMessages(
  conversationId: number
): Promise<{ items: MessageItem[] }> {
  const res = await api.get("/admin/messages", {
    params: { conversation_id: conversationId },
  });
  return res.data;
}

export async function getRecommendations() {
  const res = await api.get("/recommendations");
  return res.data;
}