/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  safelist: [
    // Dynamic accent-color classes used in risk checkboxes
    'accent-orange-500', 'accent-yellow-500', 'accent-green-600',
    'accent-blue-500', 'accent-purple-500', 'accent-red-600',
  ],
  plugins: [],
}
