import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Palette sampled from the Archdiocese of Kigali coat of arms.
        gray: {
          50: '#f5f8fc',
          100: '#ebf1f7',
          200: '#d8e3ee',
          300: '#bdcede',
          400: '#8ea5bb',
          500: '#617a93',
          600: '#435d76',
          700: '#304a63',
          800: '#1f3850',
          900: '#142d44',
          950: '#0c2033',
        },
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#2878c8',
          600: '#1d5f9f',
          700: '#174b7c',
          800: '#153d63',
          900: '#102b45',
        },
        gold: {
          50: '#fffbed',
          100: '#fff3c4',
          200: '#f8e49a',
          300: '#f2ce63',
          400: '#e8b83b',
          500: '#d9a51b',
          600: '#ae7c0d',
          700: '#81590a',
        },
        ecclesial: {
          primary: '#174b7c',
          secondary: '#d9a51b',
          dark: '#102b45',
          light: '#f5f8fc',
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
