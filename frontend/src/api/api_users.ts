import { api } from "./api";
import type { User } from "../types/User";

// --- USERS ---
export async function getUsers() {
  const res = await api.get("/users");
  return res.data;
}

export async function createUser(data: User) {
  const res = await api.post("/users", data);
  return res.data;
}

export async function updateUser(userId: number, data: User) {
  const res = await api.put(`/users/${userId}`, data);
  return res.data;
}

export async function deleteUser(userId: number) {
  const res = await api.delete(`/users/${userId}`);
  return res.data;
}

