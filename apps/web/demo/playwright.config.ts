import {defineConfig} from '@playwright/test';
// Records the captioned GitHub walkthrough; not part of the regression suite.
// Run against a fresh disposable demo (see demo/README.md) so the seeded case is unchanged.
export default defineConfig({testDir:'.',timeout:240000,workers:1,retries:0,reporter:'list',use:{
  baseURL:process.env.BANK_BASE_URL||'http://127.0.0.1:8000',headless:true,
  viewport:{width:1280,height:800},video:{mode:'on',size:{width:1280,height:800}},
  launchOptions:{slowMo:120},
}});
