/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        mint:   { bg: "#b8d4c8", dark: "#8fb5a4", mid: "#a4c4b8", light: "#d4e8e0", card: "#e8f4ef" },
        forest: { DEFAULT: "#1a3d2b", light: "#2d5a40", deep: "#0f2419" },
        coral:  { DEFAULT: "#e8614a", hover: "#d44f38", muted: "#f5c5bb" },
        warm:   "#f5f0e8",
        sqldark: "#0d2418",
      },
      fontFamily: {
        mono:  ['"Space Mono"', "Courier New", "monospace"],
        pixel: ['"VT323"', "monospace"],
      },
      borderWidth: { 3: "3px" },
      keyframes: {
        blink:      { "0%,100%": { opacity: 1 }, "50%": { opacity: 0 } },
        slideUp:    { from: { opacity: 0, transform: "translateY(8px)" }, to: { opacity: 1, transform: "translateY(0)" } },
        dotBounce:  { "0%,80%,100%": { transform: "translateY(0)" }, "40%": { transform: "translateY(-6px)" } },
      },
      animation: {
        blink:       "blink 1s step-end infinite",
        "slide-up":  "slideUp 0.2s ease-out",
        "dot-bounce":"dotBounce 1.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
}
