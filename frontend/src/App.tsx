import { useState } from "react";
import NavBar from "./components/NavBar";
import ChatLayout from "./layouts/ChatLayout";
import AdminLayout from "./layouts/AdminLayout";
// parte de las animaciones 
import { AnimatePresence } from "framer-motion";
import PageTransition from "./components/PageTransition";

export default function App() {
  const [page, setPage] = useState("chat");

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">

      {/* Navbar directamente, con sticky aplicado aquí */}
      <NavBar
        page={page}
        setPage={setPage}
        className="sticky top-0 z-50 bg-surface border-b border-border"
      />

      <AnimatePresence mode="wait">
        {page === "chat" ? (
          <PageTransition key="chat">
            <ChatLayout />
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
