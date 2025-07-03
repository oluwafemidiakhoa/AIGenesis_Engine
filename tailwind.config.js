/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    './app/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Define your primary color palette.
        // You can use any color from the Tailwind CSS color palette.
        primary: colors.sky,
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}