import {defineConfig} from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  use: {baseURL: process.env.RESEARCH_BASE_URL || 'http://127.0.0.1:8010', headless: true, trace: 'retain-on-failure'},
  reporter: 'list',
});
