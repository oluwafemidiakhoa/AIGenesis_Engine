/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js",
    "./app/**/*.py"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: 'rgb(14 165 233)', // Corresponds to sky-500
          600: 'rgb(2 132 199)',  // Corresponds to sky-600
        }
      }
    },
  },
  plugins: [],
}
