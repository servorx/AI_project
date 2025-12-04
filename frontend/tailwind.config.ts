import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ["RobotoMono", "monospace"],  // o el nombre que prefieras
      },
    },
  },
  plugins: [],
} satisfies Config;
