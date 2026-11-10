import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
const data = JSON.parse(
  readFileSync(
    new URL("../public/data/showcase.json", import.meta.url),
    "utf8",
  ),
);
const output = path.resolve(
  process.env.SHOWCASE_EVIDENCE_DIR || "../../docs/evidence/static-showcase",
);
const clean = data.experiments.find((e: { name: string }) =>
  e.name.startsWith("Clean fusion"),
);
const offset = data.experiments.find((e: { name: string }) =>
  e.name.startsWith("Offset"),
);
test.beforeEach(async ({ page }, testInfo) => {
  const errors: string[] = [];
  const failed: string[] = [];
  const unexpected: string[] = [];
  const origin = new URL(testInfo.project.use.baseURL as string).origin;
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("response", (r) => {
    if (r.status() >= 400)
      failed.push(`${r.status()} ${new URL(r.url()).pathname}`);
  });
  page.on("request", (r) => {
    const u = new URL(r.url());
    if (
      u.origin !== origin ||
      r.method() !== "GET" ||
      (!(
        u.protocol === "blob:" &&
        u.origin === origin &&
        r.resourceType() === "media"
      ) &&
        !/^\/(?:$|assets\/|data\/|reports\/|favicon\.svg$|NOTICES\.txt$)/.test(
          u.pathname,
        ))
    )
      unexpected.push(`${r.method()} ${u.origin}${u.pathname}`);
  });
  await page.addInitScript(() => {
    window.localStorage.clear();
  });
  await testInfo.attach("network-policy", {
    body: "All app runtime requests must be GETs to same-origin static assets.",
  });
  // Checked after each case without persisting arbitrary page payloads.
  active.set(testInfo.testId, { errors, failed, unexpected });
});
const active = new Map<
  string,
  { errors: string[]; failed: string[]; unexpected: string[] }
>();
test.afterEach(async ({}, info) => {
  const state = active.get(info.testId)!;
  expect(state.errors, "Browser errors").toEqual([]);
  expect(state.failed, "Missing static resources").toEqual([]);
  expect(
    state.unexpected,
    "Unexpected backend/external/mutating requests",
  ).toEqual([]);
  active.delete(info.testId);
});

test("premium landing and static navigation", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Movement. Measured. Questioned./ }),
  ).toBeVisible();
  await expect(
    page.getByText(
      "Generated fixtures. Precomputed results. No athlete accuracy claim.",
    ),
  ).toBeVisible();
  await page.screenshot({
    path: path.join(output, "landing-desktop.png"),
    fullPage: true,
  });
  await page.getByRole("link", { name: "Explore Interactive Demo" }).click();
  await expect(page.getByLabel("Shared session timeline")).toBeVisible();
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "Methodology" })
    .click();
  await expect(
    page.getByRole("heading", { name: /Make the observation/ }),
  ).toBeVisible();
});
test("actual video playback, seeking, synchronized pose and graph zoom", async ({
  page,
}) => {
  await page.goto("/#/replay");
  const video = page.locator("video");
  await expect
    .poll(() => video.evaluate((v) => (v as HTMLVideoElement).readyState))
    .toBeGreaterThanOrEqual(2);
  await page.getByRole("button", { name: "Play replay", exact: true }).click();
  await expect
    .poll(() => video.evaluate((v) => (v as HTMLVideoElement).currentTime))
    .toBeGreaterThan(0.35);
  await page.getByRole("button", { name: "Pause replay", exact: true }).click();
  await page.getByLabel("Shared session timeline").fill("5000000");
  await expect(page.getByTestId("shared-time")).toContainText("5.000 s");
  await expect
    .poll(() => video.evaluate((v) => (v as HTMLVideoElement).currentTime))
    .toBeCloseTo(5, 1);
  await expect(page.locator(".pose-foot")).toContainText("5.000 s");
  await page.getByRole("button", { name: "Zoom to 2 s" }).click();
  await expect(
    page.getByRole("button", { name: "Show full trace" }),
  ).toHaveAttribute("aria-pressed", "true");
  await page
    .getByRole("button", { name: "Seek to measured event 1 at 2.00 s" })
    .click();
  await expect(page.getByTestId("shared-time")).toContainText("2.000 s");
  await expect(page.getByText("Signals meet in time.")).toBeVisible();
  await page.getByRole("button", { name: "Seek forward 0.1 seconds" }).click();
  await expect(page.getByTestId("shared-time")).toContainText("2.100 s");
  await page.screenshot({
    path: path.join(output, "replay-desktop.png"),
    fullPage: true,
  });
});
test("clock corruption preserves undefined precision and missed-event navigation", async ({
  page,
}) => {
  await page.goto("/#/challenge");
  await page.getByLabel("Choose the evidence").selectOption(offset.id);
  await expect(page.locator(".metrics>div").nth(0)).toContainText("—");
  await expect(page.locator(".metrics>div").nth(1)).toContainText("0.0%");
  await expect(
    page.getByText("Selection never starts a new inference job."),
  ).toBeVisible();
  await page.screenshot({
    path: path.join(output, "challenge-offset-desktop.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: /Missed reference #1/ }).click();
  await expect(page.getByTestId("shared-time")).toContainText("2.000 s");
});
test("all ten scenarios show their genuine stored state", async ({ page }) => {
  await page.goto("/#/challenge");
  for (const e of data.experiments) {
    await page.getByLabel("Choose the evidence").selectOption(e.id);
    await expect(page.locator(".result-title h3")).toHaveText(
      e.name.split(" / ")[0],
    );
    if (e.status === "failed")
      await expect(
        page.getByText("No valid observation to infer from."),
      ).toBeVisible();
    else
      await expect(page.locator(".result-events>strong")).toHaveText(
        String(e.result.events.length),
      );
    if (!e.result.evaluation)
      for (const metric of await page
        .locator(".metrics strong")
        .allTextContents())
        expect(metric).toBe("—");
  }
  await page.getByRole("button", { name: /A \/ VISUAL/ }).click();
  await expect(page.locator(".result-title h3")).toHaveText("Clean video");
});
test("comparison uses selectable stored results and actual event markers", async ({
  page,
}) => {
  await page.goto("/#/compare");
  await expect(page.locator(".selection input:checked")).toHaveCount(3);
  await expect(page.locator(".comparison-table")).toContainText("0.0%");
  await page
    .getByLabel("Compare Offset +1 second / synthetic failure case")
    .uncheck();
  await expect(page.locator(".selection input:checked")).toHaveCount(2);
  await page
    .getByLabel("Compare Missing IMU window / synthetic failure case")
    .check();
  await expect(page.locator(".comparison-table")).toContainText("50.0%");
  await page.screenshot({
    path: path.join(output, "comparison-desktop.png"),
    fullPage: true,
  });
  await page.locator(".event-lane a").first().click();
  await expect(page.getByLabel("Shared session timeline")).toBeVisible();
});
test("report, JSON and Markdown exports retain actual evaluations", async ({
  page,
}) => {
  await page.goto(`/#/report/${clean.id}`);
  await expect(
    page.getByRole("heading", { name: clean.name, exact: true }),
  ).toBeVisible();
  await expect(page.locator(".report")).toContainText("independence false");
  const jsonWait = page.waitForEvent("download");
  await page.getByRole("link", { name: "JSON", exact: true }).click();
  const jsonFile = await jsonWait;
  const exported = JSON.parse(await readFile((await jsonFile.path())!, "utf8"));
  expect(exported.experiment.result).toEqual(clean.result);
  expect(exported.reference.manifest.independent).toBe(false);
  const mdWait = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download Markdown" }).click();
  const md = await readFile((await (await mdWait).path())!, "utf8");
  expect(md).toContain("not real-world model accuracy");
  expect(md).toContain(clean.fingerprint);
  await page.screenshot({
    path: path.join(output, "report-desktop.png"),
    fullPage: true,
  });
  await page.pdf({
    path: path.join(output, "experiment-report.pdf"),
    printBackground: true,
  });
});
test("hash deep links, refresh and unknown routes", async ({ page }) => {
  await page.goto("/#/replay?t=5");
  await expect(page.getByTestId("shared-time")).toContainText("5.000 s");
  await page.reload();
  await expect(page.getByTestId("shared-time")).toContainText("5.000 s");
  await page.goto(`/#/report/${clean.id}`);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: clean.name, exact: true }),
  ).toBeVisible();
  await page.goto("/#/unknown");
  await expect(
    page.getByText("This view isn’t in the snapshot."),
  ).toBeVisible();
});
test("mobile navigation, all major layouts and video seek", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  for (const [route, name] of [
    ["/", "landing"],
    ["/replay", "replay"],
    ["/challenge", "challenge"],
    ["/compare", "compare"],
    ["/methodology", "methodology"],
    [`/report/${clean.id}`, "report"],
  ]) {
    await page.goto("/#" + route);
    await expect(page.locator("h1").first()).toBeVisible();
    await page.waitForTimeout(150);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
      `${name} overflow`,
    ).toBe(true);
    await page.screenshot({
      path: path.join(output, `${name}-mobile.png`),
      fullPage: true,
    });
  }
  await page.goto("/#/replay");
  await page.getByLabel("Shared session timeline").fill("3000000");
  await expect(page.getByTestId("shared-time")).toContainText("3.000 s");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page
    .getByRole("navigation")
    .getByRole("link", { name: "Compare", exact: true })
    .click();
  await expect(page.locator(".comparison-table")).toBeVisible();
});
test("loading failure offers a real retry", async ({ page }) => {
  // Deliberately injected response is expected; it is not a missing production asset.
  await page.route("**/data/showcase.json", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "{}" }),
  );
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText("could not be verified");
  await page.unroute("**/data/showcase.json");
  await page.getByRole("button", { name: "Retry loading" }).click();
  await expect(
    page.getByRole("link", { name: "Explore Interactive Demo" }),
  ).toBeVisible();
});
