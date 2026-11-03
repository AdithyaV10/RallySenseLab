import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  timeout: 120000,
  expect: { timeout: 20000 },
  workers: 1,
  fullyParallel: false,
  use: {
    baseURL: process.env.TEST_BASE_URL || "http://127.0.0.1:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1440, height: 1000 },
      },
    },
  ],
  reporter: [["list"], ["json", { outputFile: "test-results/report.json" }]],
});
