/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef7f6',
          100: '#d3ece8',
          200: '#a7d9d1',
          300: '#71bfb2',
          400: '#3f9d8e',
          500: '#1E7A6F', // primary teal
          600: '#166258',
          700: '#124f47',
          800: '#0F3D5C', // deep navy accent
          900: '#0a2a3f',
        },
        amber: {
          accent: '#E8A33D',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        panel: '0 1px 3px rgba(15, 61, 92, 0.08), 0 1px 2px rgba(15, 61, 92, 0.06)',
      },
    },
  },
  plugins: [],
}
