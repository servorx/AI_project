import { motion } from 'framer-motion'

export default function ChatHeader() {
  return (
    <motion.div
      initial={{ y: -12, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="px-8 py-4 border-b border-border bg-surface sticky top-19 z-40"
    >
      <h2 className="text-lg font-semibold text-text-primary">
        Chat con el Asistente
      </h2>
    </motion.div>
  )
}
