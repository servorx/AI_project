import { useState } from "react";
import NavBar from "./components/NavBar";
import ChatLayout from "./layouts/ChatLayout";
import AdminLayout from "./layouts/AdminLayout";
// parte de las animaciones 
import { AnimatePresence } from "framer-motion";
import PageTransition from "./components/PageTransition";

const DEFAULT_SESSION_ID = () => `web_${Math.random().toString(36).slice(2, 9)}`;

export default function App() {
  const [page, setPage] = useState("chat");
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem("ac_session_id");
    if (stored) return stored;
    const id = DEFAULT_SESSION_ID();
    localStorage.setItem("ac_session_id", id);
    return id;
  });

  return (
    <div className="h-screen flex flex-col bg-background">
      <NavBar page={page} setPage={setPage} />

      <AnimatePresence mode="wait">
        {page === "chat" ? (
          <PageTransition key="chat">
            <ChatLayout sessionId={sessionId} />
          </PageTransition>
        ) : (
          <PageTransition key="admin">
            <AdminLayout />
          </PageTransition>
        )}
      </AnimatePresence>
    </div>
  );
}