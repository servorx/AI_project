import { motion } from "framer-motion";
import type { Variants } from "framer-motion";

const dotVariants: Variants = {
  pulse: {
    scale: [1, 1.5, 1],
    transition: {
      duration: 1.2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

export default function LoadingThreeDotsPulse() {
  return (
    <motion.div
      className="flex items-center justify-center gap-5"
      animate="pulse"
      transition={{ staggerChildren: 0.2 }}
    >
      <motion.span
        className="w-5 h-5 rounded-full bg-white"
        variants={dotVariants}
      />
      <motion.span
        className="w-5 h-5 rounded-full bg-white"
        variants={dotVariants}
      />
      <motion.span
        className="w-5 h-5 rounded-full bg-white"
        variants={dotVariants}
      />
    </motion.div>
  );
};
