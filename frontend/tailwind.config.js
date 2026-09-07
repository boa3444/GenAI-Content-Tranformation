/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/remotion/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FFFFFF",
        surface: "#F8F9FA",
        "surface-border": "#E5E7EB",
        charcoal: {
          DEFAULT: "#0A0A0A",
          muted: "#404040",
          subtle: "#737373",
        }
      },
      borderRadius: {
        '3xl': '24px',
        '2xl': '18px',
      },
      boxShadow: {
        'studio-diffused': '0 25px 50px -12px rgba(0, 0, 0, 0.06), 0 0 1px 1px rgba(0, 0, 0, 0.04)',
        'studio-card': '0 10px 30px -5px rgba(0, 0, 0, 0.04), 0 0 1px 1px rgba(0, 0, 0, 0.03)',
      }
    },
  },
  plugins: [],
}
