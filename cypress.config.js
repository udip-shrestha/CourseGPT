const path = require('path')
const Module = require('module')
const { defineConfig } = require('cypress')

// Allow Cypress to resolve dependencies (like TypeScript) from the Frontend workspace.
const additionalNodePaths = [path.resolve(__dirname, 'Frontend/node_modules')]
process.env.NODE_PATH = additionalNodePaths
  .concat(process.env.NODE_PATH || '')
  .filter(Boolean)
  .join(path.delimiter)
Module._initPaths()

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://sdmay26-37.ece.iastate.edu/',
    specPattern: 'Frontend/cypressTests/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'Frontend/cypressTests/support/e2e.ts',
  },
})