/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
    './providers/**/*.{js,jsx,ts,tsx}',
    './hooks/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        bg: 'rgb(var(--bg))',
        panel: 'rgb(var(--panel))',
        text: 'rgb(var(--text))',
        muted: 'rgb(var(--muted))',
        accent: 'rgb(var(--accent))',
        ring: 'rgb(var(--ring))'
      },
      boxShadow: {
        soft: '0 10px 30px rgba(0,0,0,0.08)'
      }
    }
  },
  plugins: []
}
