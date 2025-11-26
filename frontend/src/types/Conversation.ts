// ese usa interface porque es un modelo de datos, no una union o composicion
export interface Conversation {
  id: number;
  user_phone?: string | null;
  session_id?: string | null;
  created_at: string;
}
