export type Message = {
  id?: string | number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at?: string;
};