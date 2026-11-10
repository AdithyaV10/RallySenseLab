import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

const data = JSON.parse(
  readFileSync(
    new URL("../public/data/showcase.json", import.meta.url),
    "utf8",
  ),
);

async function synchronized(
  page: import("@playwright/test").Page,
  seconds: number,
) {
  await expect
    .poll(() =>
      page
        .locator("video")
        .evaluate((v) => (v as HTMLVideoElement).currentTime),
    )
    .toBeCloseTo(seconds, 2);
  await expect(page.getByTestId("shared-time")).toContainText(
    seconds.toFixed(3) + " s",
  );
  expect(
    Math.abs(
      Number.parseFloat(await page.locator(".pose-foot .mono").innerText()) -
        seconds,
    ),
  ).toBeLessThanOrEqual(0.0171);
  const cursor = Number(
    await page
      .locator(".timeline-panel .signal")
      .first()
      .locator("svg>line")
      .last()
      .getAttribute("x1"),
  );
  expect(cursor).toBeCloseTo(42 + (seconds / 8) * 840, 1);
}

test("mounted timestamp changes, history and manual controls synchronize actual video", async ({
  page,
}) => {
  await page.goto("/#/replay?t=2");
  await synchronized(page, 2);
  await page
    .locator("video")
    .evaluate((v) => (v.dataset.mountedIdentity = "original"));
  for (const t of [5, 3, 7]) {
    await page.evaluate((t) => {
      window.location.hash = `/replay?t=${t}`;
    }, t);
    await synchronized(page, t);
    await expect(page.locator("video")).toHaveAttribute(
      "data-mounted-identity",
      "original",
    );
  }
  for (const [direction, target] of [
    ["back", 3],
    ["back", 5],
    ["forward", 3],
    ["forward", 7],
  ] as const) {
    if (direction === "back") await page.goBack();
    else await page.goForward();
    await synchronized(page, target);
  }
  for (const t of [0, 0.1, 1.97, 2, 2.14, 4.99, 5, 7.98, 0.4, 3]) {
    await page.getByLabel("Shared session timeline").fill(String(t * 1e6));
    await synchronized(page, t);
  }
  // A clock update or unrelated UI change must not reapply the URL's old 7 s.
  await page.getByRole("button", { name: "Zoom to 2 s" }).click();
  await page.getByLabel("Playback speed").selectOption("0.5");
  await expect
    .poll(() =>
      page
        .locator("video")
        .evaluate((v) => (v as HTMLVideoElement).currentTime),
    )
    .toBeCloseTo(3, 2);
  await page.getByRole("button", { name: "Play replay", exact: true }).click();
  await page.evaluate(() => {
    window.location.hash = "/replay?t=5";
  });
  await expect
    .poll(() =>
      page
        .locator("video")
        .evaluate((v) => (v as HTMLVideoElement).currentTime),
    )
    .toBeGreaterThanOrEqual(5);
  const state = await page.locator("video").evaluate((v) => ({
    paused: (v as HTMLVideoElement).paused,
    rate: (v as HTMLVideoElement).playbackRate,
    time: (v as HTMLVideoElement).currentTime,
  }));
  expect(state.paused).toBe(false);
  expect(state.rate).toBe(0.5);
  expect(state.time).toBeLessThan(6);
  await page.getByRole("button", { name: "Pause replay", exact: true }).click();
  await page.evaluate(() => {
    window.location.hash = "/replay?t=3";
  });
  // Zoom keeps the cursor centered; restore the full trace before checking
  // its full-session coordinate in synchronized().
  await expect(page.getByTestId("shared-time")).toContainText("3.000 s");
  expect(
    Number(
      await page
        .locator(".timeline-panel .signal")
        .first()
        .locator("svg>line")
        .last()
        .getAttribute("x1"),
    ),
  ).toBeCloseTo(462, 1);
  await page.getByRole("button", { name: "Show full trace" }).click();
  await synchronized(page, 3);
  expect(
    await page.locator("video").evaluate((v) => (v as HTMLVideoElement).paused),
  ).toBe(true);
});

test("latest timestamp requested before real video metadata is ready wins", async ({
  page,
}) => {
  // Real HTTP traffic with Chromium throttling; no intercepted/mock responses.
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
  await cdp.send("Network.emulateNetworkConditions", {
    offline: false,
    latency: 1200,
    downloadThroughput: 1000000,
    uploadThroughput: 1000000,
  });
  await page.goto("/#/replay?t=2", { waitUntil: "domcontentloaded" });
  await expect(page.locator("video")).toBeAttached();
  expect(
    await page
      .locator("video")
      .evaluate((v) => (v as HTMLVideoElement).readyState),
  ).toBe(0);
  for (const t of [5, 3, 7]) {
    await page.evaluate((t) => {
      window.location.hash = `/replay?t=${t}`;
    }, t);
    await expect(page.getByTestId("shared-time")).toContainText(
      t.toFixed(3) + " s",
    );
  }
  await synchronized(page, 7);
  await page.reload();
  await synchronized(page, 7);
});

test("failure-explorer links still seek settled media after timestamp navigation", async ({
  page,
}) => {
  for (const name of ["Clean fusion", "Offset", "Missing IMU"]) {
    const experiment = data.experiments.find((e: { name: string }) =>
      e.name.startsWith(name),
    );
    await page.goto("/#/challenge");
    await page.getByLabel("Choose the evidence").selectOption(experiment.id);
    const button = page
      .locator(".failure-explorer .failure-grid button")
      .first();
    const target = Number(
      (await button.innerText()).match(/(\d+\.\d+)\s*s/)![1],
    );
    await button.click();
    await synchronized(page, target);
    await page.waitForTimeout(250);
    await synchronized(page, target);
  }
});
