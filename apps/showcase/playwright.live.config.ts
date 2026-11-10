import { defineConfig } from "@playwright/test";

const url = "https://lucky-band-a550.adithya-v1833.workers.dev";
if (process.env.SHOWCASE_URL !== url)
  throw new Error(
    "Live acceptance requires the exact approved public URL. No localhost fallback.",
  );
export default defineConfig({
  testDir: ".",
  testMatch: ["**/e2e/*.spec.ts", "**/live-tests/live.spec.ts"],
  grepInvert: /loading failure offers a real retry/,
  workers: 1,
  timeout: 45000,
  retries: 0,
  reporter: [
    ["list"],
    [
      "json",
      {
        outputFile: `${process.env.SHOWCASE_EVIDENCE_DIR || "../../docs/evidence/live-showcase"}/playwright-results.json`,
      },
    ],
  ],
  outputDir: "../../storage/live-showcase/playwright",
  use: {
    baseURL: url,
    browserName: "chromium",
    viewport: { width: 1440, height: 1000 },
    ignoreHTTPSErrors: false,
    serviceWorkers: "block",
    trace: "retain-on-failure",
  },
});
