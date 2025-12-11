import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getRecommendations } from "../../api/api_recomendations";
import type { Product } from "../../types/Product";
import type { Guide } from "../../types/Guide";

export default function ChatSidebar() {
  const [products, setProducts] = useState<Product[]>([]);
  const [guides, setGuides] = useState<Guide[]>([]);
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
      className="w-2/6 bg-surface border-l border-border p-4 hidden lg:flex flex-col overflow-y-auto"
    >
    <h2 className="text-lg font-semibold text-text-primary mb-4">
      Recomendaciones
    </h2>

    {loading ? (
    <div className="animate-pulse space-y-3">
      <div className="h-4 bg-border rounded" />
      <div className="h-4 bg-border rounded" />
    </div>
    ) : (
      <div className="space-y-4">
        {products.map((p) => (
          <motion.div
            key={p.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="bg-background border border-border rounded-lg p-3 hover:border-primary transition cursor-pointer"
          >
            {p.image && (
              <img
                src={p.image}
                alt={p.name}
                className="w-full rounded mb-2 opacity-90 hover:opacity-100 transition"
              />
            )}
            <div className="text-text-primary font-medium text-sm">
              {p.name}
            </div>
            <div className="text-text-secondary text-xs mb-1">
              {p.desc}
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-secondary font-semibold">
                ${p.price}
              </span>
              <div>
                <span className="text-text-primary mr-1">
                  switch: 
                </span>
                <span className="text-primary">
                  {p.switch}
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    )}

    <h2 className="text-lg font-semibold text-text-primary mt-6 mb-3">
      Guías rápidas
    </h2>

    {guides.map((g, i) => (
      <motion.div
        key={i}
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.25 }}
        className="p-3 bg-background border border-border rounded-lg mb-2"
      >
        <div className="text-text-primary text-sm font-medium">
          {g.title}
        </div>
        <div className="text-text-secondary text-xs mt-1">
          {g.content}
        </div>
      </motion.div>
    ))}
    </aside>
  );
}