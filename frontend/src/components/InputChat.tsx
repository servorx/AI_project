import { motion } from "framer-motion";
import Loader from "./Loader";

interface Props {
  input: string;
  setInput: (v: string) => void;
  loading: boolean;
  onSend: () => void;
}

export default function InputChat({ input, setInput, loading, onSend }: Props) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSend();
      }}
      className="p-4 border-t border-border bg-surface flex gap-3"
    >
      <input
        className="
          flex-1 
          bg-background 
          border border-border 
          rounded-md px-3 py-2 
          text-text-primary
          placeholder-text-secondary
          focus:ring-2 focus:ring-primary 
          duration-200
        "
        placeholder="Escribe tu mensaje…"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={loading}
      />

      <motion.button
        whileTap={{ scale: 0.95 }}
        whileHover={{ scale: 1.03 }}
        disabled={loading}
        className="
          bg-primary
          text-white 
          px-4 py-2 rounded-md 
          shadow-md disabled:opacity-50
        "
      >
        {loading ? <Loader /> : "Enviar"}
      </motion.button>
    </form>
  );
}
