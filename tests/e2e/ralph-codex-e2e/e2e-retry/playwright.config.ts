import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: 'node src/server.js',
    port: 3000,
    reuseExistingServer: false,
  },
});
