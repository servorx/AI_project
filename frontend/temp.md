import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { motion, AnimatePresence } from "framer-motion";

// NOTE: This file is meant to be used as src/App.tsx inside a Vite + React + TS project.
// It implements a small SPA with two pages: Chat (cliente) y Admin (read-only).
// It uses Tailwind CSS utility classes and Framer Motion for animations.

// -----------------------------
// Config
// -----------------------------
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000"; // Exponer en .env
const DEFAULT_SESSION_ID = () => `web_${Math.random().toString(36).slice(2, 9)}`;

// -----------------------------
// Types
// -----------------------------
type Message = {
  id?: string | number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at?: string;
};

// -----------------------------
// Utils
// -----------------------------
function timeNowISO() {
  return new Date().toISOString();
}

// -----------------------------
// Components
// -----------------------------

function Navbar({ page, setPage }: { page: string; setPage: (p: string) => void }) {
  return (
    <nav className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-md bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center text-white font-bold">AC</div>
        <div>
          <div className="font-semibold">Asistente Comercial</div>
          <div className="text-xs text-slate-500">Vendedor de teclados mecánicos — Español (Col)</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={() => setPage("chat")}
          className={`px-3 py-1 rounded-md ${page === "chat" ? "bg-indigo-50 text-indigo-700" : "text-slate-600 hover:bg-slate-50"}`}
        >
          Chat
        </button>
        <button
          onClick={() => setPage("admin")}
          className={`px-3 py-1 rounded-md ${page === "admin" ? "bg-indigo-50 text-indigo-700" : "text-slate-600 hover:bg-slate-50"}`}
        >
          Admin (read-only)
        </button>
        <a className="ml-2 text-xs text-slate-400">{new Date().toLocaleDateString()}</a>
      </div>
    </nav>
  );
}

function ChatBubble({ m }: { m: Message }) {
  const isUser = m.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      className={`max-w-[80%] p-3 rounded-lg my-1 ${isUser ? "bg-indigo-600 text-white ml-auto" : "bg-slate-100 text-slate-900"}`}
    >
      <div className="whitespace-pre-line">{m.content}</div>
      <div className={`text-[10px] mt-2 ${isUser ? "text-indigo-100" : "text-slate-400"}`}>{m.created_at ? new Date(m.created_at).toLocaleTimeString() : ""}</div>
    </motion.div>
  );
}

function ChatPage({ sessionId }: { sessionId: string }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "system", content: "Hola 👋 Soy tu asistente de teclados mecánicos. ¿En qué te ayudo?", created_at: timeNowISO() }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text: string) {
    if (!text.trim()) return;
    const userMsg: Message = { role: "user", content: text, created_at: timeNowISO() };
    setMessages((s) => [...s, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch(`${API_BASE}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          session_id: sessionId,
        },
        body: JSON.stringify({ message: text }),
      });
      const data = await resp.json();
      const assistantMsg: Message = { role: "assistant", content: data.response ?? "Lo siento, no entendí.", created_at: timeNowISO() };
      setMessages((s) => [...s, assistantMsg]);
    } catch (err) {
      console.error(err);
      const failMsg: Message = { role: "assistant", content: "Error: no se pudo conectar con el servidor.", created_at: timeNowISO() };
      setMessages((s) => [...s, failMsg]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="px-6 py-4 border-b bg-gradient-to-r from-indigo-50 to-white">
        <h2 className="text-lg font-semibold">Chat con el Asistente</h2>
        <p className="text-sm text-slate-500">Sesión: <span className="font-mono">{sessionId}</span></p>
      </div>

      <div ref={scrollerRef} className="flex-1 overflow-auto p-6 space-y-3 bg-gradient-to-b from-white to-slate-50">
        <AnimatePresence initial={false} mode="popLayout">
          {messages.map((m, i) => (
            <ChatBubble key={i} m={m} />
          ))}
        </AnimatePresence>
      </div>

      <div className="p-4 border-t bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage(input);
          }}
          className="flex gap-3 items-center"
        >
          <input
            className="flex-1 border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="Escribe tu mensaje... (ej: Quiero un teclado TKL para programar, presupuesto 150 USD)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="px-4 py-2 rounded-md bg-indigo-600 text-white hover:bg-indigo-700" disabled={loading}>
            {loading ? "Enviando..." : "Enviar"}
          </button>
        </form>
      </div>
    </div>
  );
}

function AdminPage() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [selectedConv, setSelectedConv] = useState<number | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  async function loadConversations() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/admin/conversations`);
      const data = await res.json();
      setConversations(data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function loadMessages(convId: number) {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/admin/messages?conversation_id=${convId}`);
      const data = await res.json();
      setMessages(data.items || []);
      setSelectedConv(convId);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadConversations();
  }, []);

  return (
    <div className="flex-1 h-full flex">
      <div className="w-80 border-r bg-white p-4 overflow-auto">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Conversaciones</h3>
          <button onClick={loadConversations} className="text-xs text-indigo-600">Actualizar</button>
        </div>
        <div className="space-y-2">
          {conversations.length === 0 && !loading && <div className="text-sm text-slate-500">No hay conversaciones</div>}
          {conversations.map((c) => (
            <motion.div
              key={c.id}
              whileHover={{ scale: 1.01 }}
              onClick={() => loadMessages(c.id)}
              className="p-3 rounded-md hover:bg-slate-50 cursor-pointer flex flex-col"
            >
              <div className="text-sm font-medium">{c.user_phone || c.session_id}</div>
              <div className="text-xs text-slate-400">{new Date(c.created_at).toLocaleString()}</div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="flex-1 p-4 overflow-auto bg-slate-50">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold">Mensajes</h3>
          {selectedConv && <div className="text-sm text-slate-500">Conversation #{selectedConv}</div>}
        </div>

        <div className="space-y-3">
          {messages.length === 0 && <div className="text-sm text-slate-500">Selecciona una conversación a la izquierda</div>}
          {messages.map((m) => (
            <div key={m.id} className={`p-3 rounded-md ${m.role === "user" ? "bg-white" : "bg-indigo-50"}`}>
              <div className="text-xs text-slate-400">{m.role} • {new Date(m.created_at).toLocaleString()}</div>
              <div className="mt-1 text-sm whitespace-pre-line">{m.content}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AppShell() {
  const [page, setPage] = useState<string>("chat");
  const [sessionId, setSessionId] = useState<string>(() => {
    const stored = localStorage.getItem("ac_session_id");
    if (stored) return stored;
    const id = DEFAULT_SESSION_ID();
    localStorage.setItem("ac_session_id", id);
    return id;
  });

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <Navbar page={page} setPage={setPage} />
      <main className="flex-1">
        <div className="max-w-5xl mx-auto h-full shadow-sm mt-6 bg-white rounded-lg overflow-hidden">
          {page === "chat" ? <ChatPage sessionId={sessionId} /> : <AdminPage />}
        </div>
      </main>
    </div>
  );
}

// -----------------------------
// Render (for Vite)
// -----------------------------
const root = document.getElementById("root");
if (root) {
  createRoot(root).render(<AppShell />);
}

export default AppShell;

# 🔄 Animaciones avanzadas — Loaders, Transiciones y Skeletons

A continuación se agregan componentes profesionales de animación basados en **Framer Motion**, optimizados para tu asistente comercial. Puedes copiarlos directamente en tu carpeta `src/components` o donde prefieras.

---
## 📁 `src/components/Loader.tsx`
```tsx
import { motion } from "framer-motion";

export default function Loader() {
  return (
    <div className="flex items-center justify-center py-4">
      <motion.div
        className="w-3 h-3 bg-indigo-600 rounded-full mx-1"
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 0.6, repeat: Infinity }}
      />
      <motion.div
        className="w-3 h-3 bg-indigo-600 rounded-full mx-1"
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 0.6, delay: 0.2, repeat: Infinity }}
      />
      <motion.div
        className="w-3 h-3 bg-indigo-600 rounded-full mx-1"
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 0.6, delay: 0.4, repeat: Infinity }}
      />
    </div>
  );
}
```
---
## 📁 `src/components/Skeleton.tsx`
```tsx
import { motion } from "framer-motion";

export default function Skeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="animate-pulse space-y-2">
      {[...Array(lines)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: i * 0.1 }}
          className="h-3 bg-slate-200 rounded w-full"
        />
      ))}
    </div>
  );
}
```

---
## 📁 `src/components/PageTransition.tsx`
```tsx
import { motion } from "framer-motion";
import { ReactNode } from "react";

export default function PageTransition({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.25 }}
      className="h-full"
    >
      {children}
    </motion.div>
  );
}
```

---
## 📁 Integración en ChatLayout — reemplazar loader actual
### Reemplaza:
```tsx
{loading ? "Enviando..." : "Enviar"}
```
### Por:
```tsx
{loading ? <Loader /> : "Enviar"}
```

Y agrega el import:
```tsx
import Loader from "../components/Loader";
```

---
## 📁 Integración en AdminLayout — Skeleton mientras carga
En `AdminLayout.tsx`, dentro del listado de conversaciones, reemplaza el contenido mientras `loading === true`:

```tsx
{loading && <Skeleton lines={4} />}
```

Import:
```tsx
import Skeleton from "../components/Skeleton";
```

---
## 📁 Transición entre páginas (Chat/Admin)
En `App.tsx`, reemplaza:
```tsx
{page === "chat" ? <ChatLayout sessionId={sessionId} /> : <AdminLayout />}
```
Por:
```tsx
import { AnimatePresence } from "framer-motion";
import PageTransition from "./components/PageTransition";

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
```

---
# ✔️ Resultado final
Ahora tu frontend incluye:

### ✨ Loaders animados estilo "typing indicators"  
### ✨ Skeletons profesionales para carga inicial  
### ✨ Transiciones suaves entre páginas  
### ✨ Animaciones sutiles en burbujas y listas

Si quieres, puedo agregar:
- animaciones al escribir texto tipo "typewriter", 
- transición del mensaje del bot letra por letra,
- animaciones 3D o parallax,
- microinteracciones al hacer hover.

¿Deseas animación tipo *“typing effect”* para las respuestas del asistente?


# 📌 Sidebar del 30% — Productos Recomendados + Guías Rápidas (Conectado al Backend)
A continuación se agrega un **sidebar profesional**, respetando tu estética dark y tus colores del theme. Incluye:
- Componentes React + TS individuales
- Endpoint en el backend
- Estilo coherente con Tailwind + tus variables CSS
- Diseño responsivo
- Animaciones suaves con Framer Motion

---
## 🧩 **Backend: Nuevo Endpoint `/recommendations`**
> Este endpoint devuelve productos + guías provenientes de tu KB.

📁 **`routes/admin.py` o crear `routes/recommendations.py`:**
```python
from fastapi import APIRouter
from app.services.rag_service import get_recommendations

router = APIRouter()

@router.get("/recommendations")
async def recommendations():
    return await get_recommendations()
```

📁 **`services/rag_service.py`** — ejemplo mínimo
```python
async def get_recommendations():
    # RAG real si quieres, o datos base desde tu colección
    products = [
        {
            "id": 1,
            "name": "Keychron K6",
            "desc": "Teclado 65% ideal para programar, compacto y hot-swap.",
            "price": 89,
            "switch": "Brown",
            "image": "/static/k6.png"
        },
        {
            "id": 2,
            "name": "Royal Kludge RK84",
            "desc": "TKL inalámbrico, excelente calidad/precio.",
            "price": 65,
            "switch": "Red",
            "image": "/static/rk84.png"
        }
    ]

    guides = [
        {
            "title": "¿Qué es un switch?",
            "content": "Es el mecanismo debajo de cada tecla que define la sensación al escribir."
        },
        {
            "title": "Formatos de teclado",
            "content": "Full-size, TKL, 75%, 65%, 60%. Cada uno elimina secciones para ahorrar espacio."
        }
    ]

    return {"products": products, "guides": guides}
```

---
# 🎨 **Frontend — Sidebar 30% (`src/components/Sidebar.tsx`)**
Respetando tu estilo:
- Fondo `var(--color-surface)`
- Bordes `var(--color-border)`
- Texto claro `var(--color-text-primary)`
- Acentos `var(--color-primary)` y `var(--color-secondary)`

📁 **`src/components/Sidebar.tsx`**
```tsx
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getRecommendations } from "../api/api";

export default function Sidebar() {
  const [products, setProducts] = useState<any[]>([]);
  const [guides, setGuides] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getRecommendations();
        setProducts(data.products || []);
        setGuides(data.guides || []);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <aside
      className="w-[30%] bg-[var(--color-surface)] border-l border-[var(--color-border)] p-4 hidden lg:flex flex-col overflow-y-auto"
    >
      <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
        Recomendaciones
      </h2>

      {loading ? (
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-[var(--color-border)] rounded" />
          <div className="h-4 bg-[var(--color-border)] rounded" />
        </div>
      ) : (
        <div className="space-y-4">
          {products.map((p) => (
            <motion.div
              key={p.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-3 hover:border-[var(--color-primary)] transition cursor-pointer"
            >
              {p.image && (
                <img
                  src={p.image}
                  alt={p.name}
                  className="w-full rounded mb-2 opacity-90 hover:opacity-100 transition"
                />
              )}
              <div className="text-[var(--color-text-primary)] font-medium text-sm">
                {p.name}
              </div>
              <div className="text-[var(--color-text-secondary)] text-xs mb-1">
                {p.desc}
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-[var(--color-secondary)] font-semibold">
                  ${p.price}
                </span>
                <span className="text-[var(--color-primary)]">
                  {p.switch}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mt-6 mb-3">
        Guías rápidas
      </h2>

      {guides.map((g, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.25 }}
          className="p-3 bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg mb-2"
        >
          <div className="text-[var(--color-text-primary)] text-sm font-medium">
            {g.title}
          </div>
          <div className="text-[var(--color-text-secondary)] text-xs mt-1">
            {g.content}
          </div>
        </motion.div>
      ))}
    </aside>
  );
}
```

---
# 🧩 **Frontend — API para recomendaciones**
📁 **`src/api/api.ts`**
```ts
export async function getRecommendations() {
  const res = await fetch(`${API_BASE}/recommendations`);
  return res.json();
}
```

---
# 🔗 **Integración con el ChatLayout**
Modifica tu layout principal para incluir el sidebar.

📁 **`src/layouts/ChatLayout.tsx`** → reemplaza wrapper general
```tsx
return (
  <div className="flex-1 flex h-full">
    <div className="flex-1 flex flex-col">  
      {/* Chat core */}
      <div className="px-6 py-4 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">Chat con el Asistente</h2>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Sesión: <span className="font-mono">{sessionId}</span>
        </p>
      </div>

      <div ref={scrollerRef} className="flex-1 overflow-auto p-6 space-y-3 bg-[var(--color-background)]">
        <AnimatePresence mode="popLayout">
          {messages.map((m, i) => (
            <ChatBubble key={i} m={m} />
          ))}
        </AnimatePresence>
      </div>

      <form onSubmit={...} className="p-4 border-t border-[var(--color-border)] bg-[var(--color-surface)] flex gap-3">
        ...
      </form>
    </div>

    {/* Sidebar */}
    <Sidebar />
  </div>
);
```

---
# ✔️ **Sidebar Final: Elegante, Útil, Conectado al Backend y Coherente con tu Tema**
Incluye:
- Productos con fotos, precio y switch
- Guías útiles para usuarios nuevos
- Estética dark pro
- Animaciones suaves
- 30% del ancho
- Responsive (se oculta en móvil)

Si quieres, puedo agregarte ahora:
✅ versión colapsable (toggle)  
✅ iconografía lucide-react  
✅ integración con “añadir al carrito/favoritos”  
✅ filtrado por precio/switch/formato

¿Qué opción quieres implementar después?