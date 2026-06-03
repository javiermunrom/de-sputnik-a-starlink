/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        void: '#050816',
        deep: '#08111f',
        lunar: '#e6edf7',
        mist: '#aebbd0',
        aurora: '#66e3ff',
        plasma: '#ffb86b',
        'usa-blue': '#4aa3ff',
        'russia-red': '#ff5b6e',
        'china-gold': '#ffd166',
        'europe-cyan': '#5eead4',
        'india-green': '#86efac',
        private: '#c084fc',
        public: '#60a5fa',
      },
      fontFamily: {
        display: ['Space Grotesk', 'Inter', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['IBM Plex Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      maxWidth: {
        story: '72rem',
        read: '44rem',
      },
      boxShadow: {
        glow: '0 0 60px rgba(102, 227, 255, 0.12)',
        panel: '0 24px 80px rgba(0, 0, 0, 0.35)',
      },
    },
  },
  plugins: [],
};
