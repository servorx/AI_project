import { api } from "./api";

// obtner recomendaciones
export async function getRecommendations() {
  const res = await api.get("/recommendations");
  return res.data;
}
