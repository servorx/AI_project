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