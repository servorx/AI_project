// se usa type porque es una composicion de datos 
export type Message = {
  id?: string | number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at?: string;
};