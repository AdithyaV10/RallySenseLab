// LOCAL replacement regression only. Never production acceptance evidence.
import { chromium } from "../apps/showcase/node_modules/playwright/index.mjs";
import { expect } from "../apps/showcase/node_modules/@playwright/test/index.mjs";
import AxeBuilder from "../apps/showcase/node_modules/@axe-core/playwright/dist/index.mjs";
import fs from "node:fs";
const origin = "http://127.0.0.1:14173";
const out = "docs/evidence/live-showcase/replacement";
const data = JSON.parse(
  fs.readFileSync("apps/showcase/public/data/showcase.json", "utf8"),
);
const clean = data.experiments.find((e) => e.name.startsWith("Clean fusion"));
const browser = await chromium.launch();
const context = await browser.newContext();
const page = await context.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
try {
  await page.goto(origin + "/#/replay?t=5");
  const video = page.locator("video");
  await expect
    .poll(() => video.evaluate((v) => v.currentTime))
    .toBeCloseTo(5, 2);
  const loaded = await video.evaluate((v) => ({
    source_protocol: new URL(v.currentSrc).protocol,
    seekable_end: v.seekable.end(0),
  }));
  expect(loaded.source_protocol).toBe("blob:");
  expect(loaded.seekable_end).toBeGreaterThan(7.9);
  const seeks = [];
  for (const t of [0, 0.1, 1.97, 2, 2.14, 4.99, 5, 7.98, 0.4, 3]) {
    await page.getByLabel("Shared session timeline").fill(String(t * 1e6));
    await expect
      .poll(() => video.evaluate((v) => v.currentTime))
      .toBeCloseTo(t, 2);
    const pose = Number.parseFloat(
      await page.locator(".pose-foot .mono").innerText(),
    );
    expect(Math.abs(pose - t)).toBeLessThanOrEqual(0.0171);
    seeks.push({ target: t, pose });
  }
  await page.getByRole("button", { name: "Play replay", exact: true }).click();
  await expect
    .poll(() => video.evaluate((v) => v.currentTime))
    .toBeGreaterThan(3.2);
  await page.getByRole("button", { name: "Pause replay", exact: true }).click();
  const layouts = [];
  for (const [viewport, width, height] of [
    ["desktop", 1440, 1000],
    ["phone", 390, 844],
    ["tablet", 820, 1180],
  ]) {
    await page.setViewportSize({ width, height });
    for (const [route, label] of [
      ["/", "landing"],
      ["/replay", "replay"],
      ["/challenge", "challenge"],
      ["/compare", "comparison"],
      ["/methodology", "methodology"],
      [`/report/${clean.id}`, "report"],
    ]) {
      await page.goto(origin + "/#" + route, { waitUntil: "networkidle" });
      const result = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        .analyze();
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth + 1,
      );
      layouts.push({
        viewport,
        route,
        overflow,
        violations: result.violations.map((v) => ({
          id: v.id,
          nodes: v.nodes.map((n) => n.target),
        })),
      });
      await page.screenshot({
        path: `${out}/${label}-${viewport}.png`,
        fullPage: true,
      });
    }
  }
  fs.writeFileSync(
    `${out}/local-regression.json`,
    JSON.stringify(
      {
        scope: "LOCAL REPLACEMENT ONLY - NOT LIVE ACCEPTANCE",
        loaded,
        seeks,
        layouts,
        errors,
      },
      null,
      2,
    ),
  );
  expect(errors).toEqual([]);
  expect(layouts.filter((r) => r.overflow || r.violations.length)).toEqual([]);
  console.log(
    JSON.stringify({
      scope: "LOCAL REPLACEMENT ONLY",
      deep_link: true,
      seeks: seeks.length,
      layout_accessibility_checks: layouts.length,
      violations: 0,
      public_redeployment_verified: false,
    }),
  );
} finally {
  await browser.close();
}
