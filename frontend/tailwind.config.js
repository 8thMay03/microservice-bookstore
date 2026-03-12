/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ["Playfair Display", "Georgia", "Cambria", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        stone: {
          50: "#fafaf9",
        },
        brand: {
          red: "#e8392a",
        },
      },
      aspectRatio: {
        book: "3 / 4",
      },
    },
  },
  plugins: [],
};
