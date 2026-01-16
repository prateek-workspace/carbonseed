const { fontFamily } = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary palette - white dominant
        'surface': '#FAFAFA',
        'surface-elevated': '#FFFFFF',
        'surface-muted': '#F5F5F5',
        // Text hierarchy
        'ink': '#0f0f0f',
        'ink-muted': '#525252',
        'ink-faint': '#a3a3a3',
        // Accent colors (Notion-like restraint)
        'accent-blue': '#64748b',      // Muted blue-gray (data, trust)
        'accent-green': '#059669',     // Soft green (efficiency, sustainability)
        'accent-amber': '#d97706',     // Warm amber (alerts, emphasis)
        // Borders
        'border': '#e5e5e5',
        'border-muted': '#f0f0f0',
      },
      fontFamily: {
        sans: ['var(--font-inter)', ...fontFamily.sans],
        mono: ['var(--font-space-grotesk)', ...fontFamily.mono],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
      transitionTimingFunction: {
        'ease-out-expo': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
}
