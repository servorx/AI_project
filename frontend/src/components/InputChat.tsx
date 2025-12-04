import { motion } from "framer-motion";
import { Paperclip, Send } from "lucide-react";
import Loader from "./Loader";
import TextareaAutosize from "react-textarea-autosize";

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
      className="
        px-4 py-3 
        border-t border-border 
        bg-surface 
        flex items-center gap-3
      "
    >
      {/* Botón Clip */}
      <motion.button
        type="button"
        whileTap={{ scale: 0.9 }}
        whileHover={{ scale: 1.15 }}
        className="
          p-2 rounded-full 
          bg-background 
          border border-border 
          text-text-secondary
          hover:text-primary hover:border-primary
          transition-all
          shadow-sm
        "
      >
        <Paperclip size={20} />
      </motion.button>

      {/* Input expandible estilo WhatsApp */}
      <div
        className="
          flex-1 
          bg-background 
          border border-border 
          rounded-2xl 
          px-4 py-2
          shadow-sm
          focus-within:ring-2 focus-within:ring-primary/40 
          transition-all
        "
      >
        <TextareaAutosize
          minRows={1}
          maxRows={5}
          className="
            w-full bg-transparent 
            text-text-primary 
            placeholder-text-secondary
            resize-none outline-none 
            text-sm
          "
          placeholder="Escribe un mensaje…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
      </div>

      {/* Botón enviar */}
      <motion.button
        type="submit"
        whileTap={{ scale: 0.92 }}
        whileHover={{ scale: 1.1 }}
        disabled={loading || !input.trim()}
        className={`
          w-11 h-11 flex items-center justify-center
          rounded-full shadow-md
          transition-all
          ${loading || !input.trim()
            ? "bg-primary/40 cursor-not-allowed"
            : "bg-primary hover:bg-primary/90"
          }
        `}
      >
        {loading ? (
          <Loader />
        ) : (
          <Send size={18} className="text-background" />
        )}
      </motion.button>
    </form>
  );
}
