import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0a",
        surface: "#1a1a1a",
        "surface-hover": "#252525",
        "surface-elevated": "#2a2a2a",
        border: "#2a2a2a",
        "border-subtle": "#1f1f1f",
        accent: "#e10600",
        "accent-hover": "#c40500",
        "accent-muted": "rgba(225, 6, 0, 0.15)",
        text: {
          primary: "#ffffff",
          secondary: "#a0a0a0",
          muted: "#666666",
          inverse: "#0a0a0a",
        },
        status: {
          active: "#22c55e",
          retired: "#6b7280",
          "active-bg": "rgba(34, 197, 94, 0.1)",
        },
        gold: "#fbbf24",
        "gold-muted": "rgba(251, 191, 36, 0.15)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      borderRadius: {
        DEFAULT: "0.5rem",
        sm: "0.25rem",
        lg: "0.75rem",
        xl: "1rem",
        full: "9999px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0, 0, 0, 0.5), 0 1px 2px rgba(0, 0, 0, 0.6)",
        "card-hover":
          "0 4px 16px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(225, 6, 0, 0.2)",
        "accent-glow": "0 0 20px rgba(225, 6, 0, 0.3)",
      },
      backgroundImage: {
        "accent-gradient": "linear-gradient(135deg, #e10600 0%, #ff3333 100%)",
        "surface-gradient":
          "linear-gradient(180deg, #1a1a1a 0%, #141414 100%)",
      },
      animation: {
        shimmer: "shimmer 1.5s infinite",
        "fade-in": "fadeIn 0.2s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
