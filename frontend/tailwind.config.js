/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'sahistra-bg': '#fcfaf8', // Warm cream / off-white
        'sahistra-text': '#1a1816', // Deep warm black
        'sahistra-accent': '#d96c5b', // Muted terracotta/coral
        'sahistra-card': '#f5f0ea', // Very subtle warm beige
      },
      fontFamily: {
        'serif': ['"Playfair Display"', 'Georgia', 'serif'], // Elegant serif
        'sans': ['"Inter"', 'system-ui', 'sans-serif'], // Clean sans-serif
      }
    },
  },
  plugins: [],
}
