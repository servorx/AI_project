# 🎨 **Frontend — Sidebar 30% (`src/components/Sidebar.tsx`)**
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