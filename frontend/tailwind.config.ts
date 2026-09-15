import type { Config } from "tailwindcss";

// The platform's design token set (PROJECT_PLAN_v2.md Section 13.1): one
// primary brand scale, one neutral gray scale, and a small set of status
// accents — reused everywhere via this theme extension, never redefined
// ad hoc on individual pages. Indigo matches the color already used for the
// "Client" layer across the project's architecture diagrams, so the brand
// reads consistently across docs, diagrams, and the product itself.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
        success: { 50: "#f0fdf4", 500: "#22c55e", 700: "#15803d" },
        warning: { 50: "#fffbeb", 500: "#f59e0b", 700: "#b45309" },
        danger: { 50: "#fef2f2", 500: "#ef4444", 700: "#b91c1c" },
        info: { 50: "#eff6ff", 500: "#3b82f6", 700: "#1d4ed8" },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
      borderRadius: {
        card: "0.75rem",
      },
    },
  },
  plugins: [],
} satisfies Config;
