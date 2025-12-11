import { motion } from "framer-motion";

interface Props {
  // estas son las propiedades que reciben el componente
  page: string; // el nombre de la pagina actual
  setPage: (p: string) => void; // la funcion para cambiar de pagina
  className?: string;  // clases adicionales para el componente
}

// esta es la funcion principal del componente
export default function NavBar({ page, setPage, className }: Props) {
  const navItems = [
    { id: "chat", label: "Chat" },
    { id: "admin", label: "Admin" },
  ];

  return (
    <motion.nav
      initial={{ opacity: 0, y: -150 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.75, ease: "easeOut" }}
      className={`
        bg-surface border-b border-border 
        px-5 py-5 flex items-center justify-between
        ${className || ""}  // aqui se aplica el sticky para el header
      `}
    >
      {/* lado izquierdo */}
      <div className="flex items-center gap-3">
        <motion.div
          whileHover={{ scale: 1.2 }}
          transition={{ type: "spring", stiffness: 250, damping: 12 }}
          className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-text-primary font-bold shadow-lg cursor-pointer"
        >
          AC
        </motion.div>

        <div>
          <div className="font-semibold text-text-primary">
            Asistente Comercial
          </div>
          <div className="text-xs text-text-secondary">
            Vendedor de teclados mecánicos — Español (Col)
          </div>
        </div>
      </div>

      {/* lado derecho de lso botones */}
      <div className="flex items-center gap-6">
        {navItems.map((item) => {
          const active = page === item.id;

          return (
            <motion.button
              key={item.id}
              onClick={() => setPage(item.id)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.97 }}
              transition={{ duration: 0.15 }}
              className={`px-4 py-2 rounded-lg font-medium transition cursor-pointer
                ${
                  active
                    ? "bg-primary/20 text-primary shadow-sm"
                    : "text-text-secondary hover:bg-surface/70"
                }`}
            >
              {item.label}
            </motion.button>
          );
        })}
      </div>
    </motion.nav>
  );
}