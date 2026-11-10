import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";

const origin = "https://lucky-band-a550.adithya-v1833.workers.dev";
const evidence = path.resolve("../../docs/evidence/live-showcase");
mkdirSync(evidence, { recursive: true });
const approved = JSON.parse(
  readFileSync("../../docs/evidence/step6_6/demo-fixtures.json", "utf8"),
);
const manifest = JSON.parse(
  readFileSync(
    process.env.SHOWCASE_EXPECTED_MANIFEST ||
      "../../docs/evidence/static-showcase/static-build-manifest.json",
    "utf8",
  ),
);
const expected = JSON.parse(readFileSync("public/data/showcase.json", "utf8"));
const clean = expected.experiments.find((e: { name: string }) =>
  e.name.startsWith("Clean fusion"),
);
const record = (name: string, data: unknown) =>
  writeFileSync(
    path.join(evidence, name),
    JSON.stringify(data, null, 2) + "\n",
  );

test("LIVE: all 28 public assets, MIME types, hashes and every report match approved evidence", async ({
  page,
}) => {
  test.setTimeout(90000);
  const first = await page.goto(origin, { waitUntil: "networkidle" });
  expect(first!.status()).toBe(200);
  expect(page.url()).toBe(origin + "/");
  const assets = [];
  const mismatches = [];
  for (const row of manifest.files) {
    const r = await page.request.get(`${origin}/${row.path}`);
    const bytes = await r.body();
    const sha = createHash("sha256").update(bytes).digest("hex");
    const mime = r.headers()["content-type"] || "";
    assets.push({
      path: row.path,
      status: r.status(),
      bytes: bytes.length,
      sha256: sha,
      mime,
      https: r.url().startsWith("https://"),
      matches_reviewed: sha === row.sha256,
    });
    if (sha !== row.sha256) mismatches.push(row.path);
    expect(r.status(), row.path).toBe(200);
    const types: Record<string, RegExp> = {
      ".html": /^text\/html/,
      ".css": /^text\/css/,
      ".js": /^(?:text|application)\/javascript/,
      ".json": /^application\/json/,
      ".mp4": /^video\/mp4/,
      ".md": /^text\/(?:markdown|plain)/,
      ".svg": /^image\/svg\+xml/,
      ".txt": /^text\/plain/,
    };
    expect(mime, row.path).toMatch(types[path.extname(row.path)]);
  }
  record("public-asset-integrity.json", { origin, assets, mismatches });
  expect(mismatches, "Deployed bytes differ from reviewed release").toEqual([]);
  const data = await (
    await page.request.get(origin + "/data/showcase.json")
  ).json();
  expect(data).toEqual(expected);
  expect(data.reference.manifest.independent).toBe(false);
  expect(data.pose.config.provenance).toBe("generated_analytical_landmarks");
  const experiments = [];
  for (const e of data.experiments) {
    const report = await (
      await page.request.get(`${origin}/reports/${e.id}.json`)
    ).json();
    expect(report.experiment).toEqual(e);
    expect(report.reference.manifest.independent).toBe(false);
    const md = await (
      await page.request.get(`${origin}/reports/${e.id}.md`)
    ).text();
    expect(md).toContain(e.fingerprint);
    expect(md).toContain("not real-world model accuracy");
    const previous = approved.curated_experiments.find(
      (a: { id: string }) => a.id === e.id,
    );
    if (previous) {
      expect(e.result.evaluation ?? null).toEqual(previous.evaluation);
      expect(e.status).toBe(previous.status);
    }
    experiments.push({
      id: e.id,
      name: e.name,
      status: e.status,
      mode: e.mode,
      evaluation: e.result.evaluation ?? null,
      json_verified: true,
      markdown_verified: true,
    });
  }
  record("public-scientific-provenance.json", {
    dataset_matches_approved: true,
    synthetic: true,
    independent: false,
    experiments,
  });
});

test("LIVE: repeated video seeks maintain real media, cursor and stored-pose synchronization", async ({
  page,
}) => {
  await page.goto(origin + "/#/replay");
  const video = page.locator("video");
  await expect
    .poll(() => video.evaluate((v) => (v as HTMLVideoElement).readyState))
    .toBeGreaterThanOrEqual(2);
  const observations = [];
  for (const seconds of [0, 0.1, 1.97, 2, 2.14, 4.99, 5, 7.98, 0.4, 3]) {
    await page
      .getByLabel("Shared session timeline")
      .fill(String(seconds * 1e6));
    await expect
      .poll(() => video.evaluate((v) => (v as HTMLVideoElement).currentTime))
      .toBeCloseTo(seconds, 2);
    await expect(page.getByTestId("shared-time")).toContainText(
      seconds.toFixed(3) + " s",
    );
    const pose = Number.parseFloat(
      await page.locator(".pose-foot .mono").innerText(),
    );
    const cursor = Number(
      await page
        .locator(".timeline-panel .signal")
        .first()
        .locator("svg>line")
        .last()
        .getAttribute("x1"),
    );
    expect(Math.abs(pose - seconds)).toBeLessThanOrEqual(0.0171);
    expect(cursor).toBeCloseTo(42 + (seconds / 8) * 840, 1);
    observations.push({
      seek_seconds: seconds,
      media_seconds: await video.evaluate(
        (v) => (v as HTMLVideoElement).currentTime,
      ),
      stored_pose_seconds: pose,
      imu_cursor_svg_x: cursor,
    });
  }
  await page.getByLabel("Playback speed").selectOption("0.5");
  expect(
    await video.evaluate((v) => (v as HTMLVideoElement).playbackRate),
  ).toBe(0.5);
  await page.getByRole("button", { name: "Play replay", exact: true }).click();
  await expect
    .poll(() => video.evaluate((v) => (v as HTMLVideoElement).currentTime))
    .toBeGreaterThan(3.2);
  await page.getByRole("button", { name: "Pause replay", exact: true }).click();
  const paused = await video.evaluate((v) => ({
    paused: (v as HTMLVideoElement).paused,
    time: (v as HTMLVideoElement).currentTime,
  }));
  expect(paused.paused).toBe(true);
  await page
    .getByRole("button", { name: "Seek to measured event 2 at 5.00 s" })
    .click();
  await expect(page.getByTestId("shared-time")).toContainText("5.000 s");
  record("public-replay-synchronization.json", {
    origin,
    repeated_seeks: observations,
    half_speed_verified: true,
    play_and_pause_verified: true,
    event_marker_navigation: true,
  });
});

test("LIVE: keyboard controls, visible focus and browser history work", async ({
  page,
}) => {
  await page.goto(origin + "/#/replay");
  await expect(page.getByLabel("Shared session timeline")).toBeVisible();
  await page.keyboard.press("Tab");
  await expect(page.locator(".skip")).toBeFocused();
  await expect(page.locator(".skip")).toBeVisible();
  const focus = await page.locator(".skip").evaluate((e) => ({
    style: getComputedStyle(e).outlineStyle,
    width: getComputedStyle(e).outlineWidth,
    color: getComputedStyle(e).outlineColor,
  }));
  expect(focus.style).not.toBe("none");
  expect(Number.parseFloat(focus.width)).toBeGreaterThanOrEqual(2);
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();
  const slider = page.getByLabel("Shared session timeline");
  await slider.focus();
  const before = Number(await slider.inputValue());
  await page.keyboard.press("ArrowRight");
  await expect(slider).toHaveValue(String(before + 10000));
  await page.getByRole("button", { name: "Play replay", exact: true }).focus();
  await page.keyboard.press("Space");
  await expect(
    page.getByRole("button", { name: "Pause replay", exact: true }),
  ).toBeVisible();
  await page.keyboard.press("Space");
  const nav = page.getByRole("navigation", { name: "Main navigation" });
  await nav.getByRole("link", { name: "Sensor Fusion Challenge" }).click();
  await nav.getByRole("link", { name: "Compare", exact: true }).click();
  await page.goBack();
  await expect(page).toHaveURL(origin + "/#/challenge");
  await page.goForward();
  await expect(page).toHaveURL(origin + "/#/compare");
  await page.goto(origin + "/#/report/unknown");
  await expect(
    page.getByRole("heading", { name: "Report not found" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Choose a stored experiment" }).click();
  await expect(page).toHaveURL(origin + "/#/compare");
  record("public-keyboard-history.json", {
    skip_link: true,
    visible_focus: focus,
    timeline_keyboard: true,
    keyboard_play_pause: true,
    back_forward: true,
    unknown_report_recovery: true,
  });
});

test("LIVE: real Print button lifecycle and generated public report PDF", async ({
  page,
}) => {
  await page.goto(`${origin}/#/report/${clean.id}`);
  await expect(
    page.getByRole("heading", { name: clean.name, exact: true }),
  ).toBeVisible();
  // Observe actual print events; do not replace or mock window.print.
  await page.evaluate(() =>
    window.addEventListener("beforeprint", () => {
      document.documentElement.dataset.printObserved = "yes";
    }),
  );
  await page.getByRole("button", { name: "Print / Save PDF" }).click();
  await expect
    .poll(() =>
      page.evaluate(() => document.documentElement.dataset.printObserved),
    )
    .toBe("yes");
  const pdf = await page.pdf({
    path: path.join(evidence, "live-experiment-report.pdf"),
    printBackground: true,
  });
  expect(pdf.subarray(0, 5).toString()).toBe("%PDF-");
  expect(pdf.length).toBeGreaterThan(10000);
  record("public-print-verification.json", {
    origin,
    print_button_fired_real_beforeprint: true,
    chromium_pdf_bytes: pdf.length,
    physical_os_print_dialog_not_inspected: true,
  });
});

test("LIVE: desktop, 390px phone and tablet layouts plus accessibility basics", async ({
  page,
}) => {
  test.setTimeout(180000);
  const rows = [];
  for (const [name, width, height] of [
    ["desktop", 1440, 1000],
    ["phone", 390, 844],
    ["tablet", 820, 1180],
  ] as const) {
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
      await expect(page.locator("h1").first()).toBeVisible();
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth + 1,
      );
      const scan = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        .analyze();
      const violations = scan.violations.map((v) => ({
        id: v.id,
        impact: v.impact,
        description: v.description,
        nodes: v.nodes.map((n) => ({
          target: n.target,
          summary: n.failureSummary,
        })),
      }));
      rows.push({
        viewport: name,
        width,
        height,
        route,
        label,
        horizontal_overflow: overflow,
        violations,
      });
      record("public-layout-accessibility.json", {
        origin,
        scope:
          "Automated WCAG 2.1 A/AA basics; not full conformance certification",
        rows,
      });
      await page.screenshot({
        path: path.join(evidence, `live-${label}-${name}.png`),
        fullPage: true,
      });
    }
  }
  expect(
    rows.filter((r) => r.horizontal_overflow),
    "Document overflow",
  ).toEqual([]);
  expect(
    rows.filter((r) => r.violations.length),
    "Accessibility/contrast violations",
  ).toEqual([]);
});

test("LIVE: network, console, privacy probes and visible action audit", async ({
  page,
}) => {
  test.setTimeout(90000);
  const errors: string[] = [],
    consoleErrors: string[] = [],
    failed: string[] = [],
    network: { method: string; url: string; type: string }[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") consoleErrors.push(m.text());
  });
  page.on("requestfailed", (r) =>
    failed.push(`${r.url()}: ${r.failure()?.errorText}`),
  );
  page.on("request", (r) =>
    network.push({ method: r.method(), url: r.url(), type: r.resourceType() }),
  );
  const emptyContextState = await page.context().storageState();
  expect(emptyContextState.cookies).toEqual([]);
  expect(emptyContextState.origins).toEqual([]);
  const actions = [];
  for (const route of [
    "/",
    "/replay",
    "/challenge",
    "/compare",
    "/methodology",
    `/report/${clean.id}`,
  ]) {
    await page.goto(origin + "/#" + route, { waitUntil: "networkidle" });
    const routeActions = await page
      .locator("button,a,input,select,summary")
      .evaluateAll((nodes) =>
        nodes
          .filter(
            (n) =>
              n.getBoundingClientRect().width &&
              n.getBoundingClientRect().height,
          )
          .map((n) => ({
            tag: n.tagName,
            text: (n.getAttribute("aria-label") || n.textContent || "")
              .trim()
              .slice(0, 160),
            href: n.getAttribute("href"),
            disabled: (n as HTMLButtonElement).disabled === true,
          })),
      );
    actions.push({ route, controls: routeActions });
  }
  const unexpected = network.filter((r) => {
    const u = new URL(r.url);
    const localMedia =
      u.protocol === "blob:" && u.origin === origin && r.type === "media";
    return (
      (!localMedia && !r.url.startsWith(origin + "/")) ||
      r.method !== "GET" ||
      /\/api(?:\/|$)|mediapipe|\.wasm|\.task|localhost|127\.0\.0\.1/i.test(
        r.url,
      )
    );
  });
  record("public-network-console.json", {
    origin,
    fresh_incognito_context: true,
    errors,
    consoleErrors,
    failed,
    unexpected,
    requests: network,
  });
  expect(errors).toEqual([]);
  expect(consoleErrors).toEqual([]);
  expect(failed).toEqual([]);
  expect(unexpected).toEqual([]);
  record("public-visible-action-inventory.json", { origin, actions });
  const probes = [];
  const index = await (await page.request.get(origin + "/")).body();
  for (const resource of [
    "/.env",
    "/.git/config",
    "/data/private/",
    "/storage/",
    "/api/v1/sessions",
    "/vendor/pose_landmarker_lite.task",
  ]) {
    const response = await page.request.get(origin + resource);
    const body = await response.body();
    const fallback = body.equals(index);
    const denied = [403, 404].includes(response.status());
    probes.push({
      path: resource,
      status: response.status(),
      mime: response.headers()["content-type"],
      same_static_html_fallback: fallback,
      denied,
    });
    expect(denied || fallback, resource + " unexpectedly exposes content").toBe(
      true,
    );
  }
  record("public-privacy-probes.json", {
    origin,
    probes,
    all_known_public_assets_match_allowlist: true,
    scope_limit:
      "Public endpoint checks cannot enumerate unlisted assets or inspect Worker/account configuration.",
  });
});
