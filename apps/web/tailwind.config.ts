import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0c0b0b",
        obsidian: "#121010",
        steel: "#938677",
        parchment: "#f3ecdf",
        bronze: "#b98958",
        ember: "#d16f4d",
        moss: "#65745f",
      },
      boxShadow: {
        panel: "0 24px 80px rgba(0, 0, 0, 0.35)",
      },
      backgroundImage: {
        noise: "radial-gradient(circle at top, rgba(185, 137, 88, 0.14), transparent 28%), linear-gradient(180deg, #171212 0%, #090808 100%)",
      },
    },
  },
  plugins: [],
};

export default config;

