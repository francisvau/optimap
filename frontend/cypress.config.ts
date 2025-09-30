import { defineConfig } from 'cypress';

export default defineConfig({
    e2e: {
        specPattern: 'test/e2e/**/*.cy.ts',
        fixturesFolder: 'test/cypress/fixtures',
        supportFile: 'test/cypress/support/e2e.ts',
        screenshotsFolder: 'test/cypress/screenshots',
    },
});
