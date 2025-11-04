/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: "media",
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          border: "var(--border)",
          input: "var(--input)",
          ring: "var(--ring)",
          background: "var(--background)",
          foreground: "var(--foreground)",
          primary: {
            DEFAULT: "var(--primary)",
            foreground: "var(--primary-foreground)",
          },
          secondary: {
            DEFAULT: "var(--secondary)",
            foreground: "var(--secondary-foreground)",
          },
          destructive: {
            DEFAULT: "var(--destructive)",
            foreground: "var(--destructive-foreground)",
          },
          muted: {
            DEFAULT: "var(--muted)",
            foreground: "var(--muted-foreground)",
          },
          accent: {
            DEFAULT: "var(--accent)",
            foreground: "var(--accent-foreground)",
          },
          card: {
            DEFAULT: "var(--card)",
            foreground: "var(--card-foreground)",
          },
          popover: {
            DEFAULT: "var(--popover)",
            foreground: "var(--popover-foreground)",
          },
        },
        borderRadius: {
          lg: "var(--radius)",
        },
        fontWeight: {
          normal: "var(--font-weight-normal)",
          medium: "var(--font-weight-medium)",
        },
        fontSize: {
          base: "18px",
        },
      },
    },
    plugins: [],
  };
  