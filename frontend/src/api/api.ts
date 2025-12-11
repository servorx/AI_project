import axios from "axios";
// importar los types 
import type { ChatResponse } from "../types/api/ChatResponse";

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

// estas son las funciones de hacer un post message para el chat del frontend
export async function postChatMessage(
  sessionId: string,
  message: string
): Promise<ChatResponse> {
  const resp = await api.post(
    "/chat",
    { message },
    { params: { session_id: sessionId } }
  );

  return resp.data;
}
