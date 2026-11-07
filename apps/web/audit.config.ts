import { defineConfig } from "@playwright/test";
import base from "./playwright.config";

// Known-defect regressions: these deliberately fail until separately authorized repairs.
export default defineConfig({
  ...base,
  testDir: "./audit",
  outputDir: "audit-results",
  reporter: [["list"], ["json", { outputFile: "audit-results/report.json" }]],
});
