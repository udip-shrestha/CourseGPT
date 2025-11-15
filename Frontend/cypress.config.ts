import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:5173",
    specPattern: "cypressTests/e2e/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: "cypressTests/support/e2e.ts",
  },
});
