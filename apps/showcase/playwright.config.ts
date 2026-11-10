import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  timeout: 30000,
  retries: 0,
  reporter: [
    ["list"],
    [
      "json",
      {
        outputFile:
          "../../docs/evidence/static-showcase/playwright-results.json",
      },
    ],
  ],
  use: {
    baseURL: process.env.SHOWCASE_URL || "http://127.0.0.1:14173",
    viewport: { width: 1440, height: 1000 },
    trace: "retain-on-failure",
  },
  webServer: process.env.SHOWCASE_URL
    ? undefined
    : {
        command: "npm run preview",
        url: "http://127.0.0.1:14173",
        reuseExistingServer: true,
        timeout: 30000,
      },
});
