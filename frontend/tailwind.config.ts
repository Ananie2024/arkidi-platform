import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Catholic Liturgical & Kigali Diocesan Color Palette
        brand: {
          50: '#fcf8f2',
          100: '#f6eedf',
          200: '#eddbc0',
          500: '#8b1e23', // Pontifical Crimson / Cardinal Red
          600: '#75171b',
          700: '#5f1115',
          900: '#340608',
        },
        gold: {
          500: '#d4af37', // Papal Gold
          600: '#b89528',
        },
        ecclesial: {
          primary: '#1e3a8a', // Marian Navy Blue
          secondary: '#8b1e23',
          dark: '#0f172a',
          light: '#f8fafc',
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
