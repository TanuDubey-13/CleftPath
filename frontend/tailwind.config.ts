import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ivory: {
          50: '#FAF7F2',
          100: '#F4EFE6',
          200: '#EBE3D5',
        },
        teal: {
          50: '#F0F7F8',
          100: '#E2EFF2',
          700: '#1C7289',
          800: '#155D70',
          900: '#0F4C5C',
          950: '#082E38',
        },
        sage: {
          100: '#EEF5F1',
          500: '#81B29A',
          600: '#6A9B84',
          700: '#52826C',
        },
        coral: {
          100: '#FAECE8',
          400: '#E89078',
          500: '#E07A5F',
          600: '#CC674C',
        },
        charcoal: {
          400: '#8A95A5',
          600: '#5A6578',
          800: '#3D4758',
          900: '#2D3748',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
        heading: ['Outfit', '"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        '2xl': '1.25rem',
        '3xl': '1.75rem',
        '4xl': '2.25rem',
      },
      boxShadow: {
        'warm-sm': '0 1px 3px 0 rgba(45, 55, 72, 0.05), 0 1px 2px 0 rgba(45, 55, 72, 0.03)',
        'warm-md': '0 4px 12px -2px rgba(45, 55, 72, 0.08), 0 2px 6px -1px rgba(45, 55, 72, 0.04)',
        'warm-lg': '0 12px 24px -4px rgba(45, 55, 72, 0.10), 0 4px 8px -2px rgba(45, 55, 72, 0.05)',
        'warm-xl': '0 20px 32px -6px rgba(45, 55, 72, 0.14), 0 8px 16px -4px rgba(45, 55, 72, 0.06)',
      },
    },
  },
  plugins: [],
} satisfies Config;
