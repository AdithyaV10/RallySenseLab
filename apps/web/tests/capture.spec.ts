import { test, expect, chromium } from "@playwright/test";
import fs from "node:fs";
async function createCollection(page: import("@playwright/test").Page) {
  await page.goto("/record");
  await page
    .getByLabel("Session title", { exact: true })
    .fill(`Synthetic browser capture ${Date.now()}`);
  await page.getByLabel("Source provenance").selectOption("synthetic");
  await page.getByLabel("Participant pseudonym").fill("software-fixture");
  await page
    .getByLabel("Movement / task")
    .fill("Synthetic injected events; not physical-device data");
  await page.getByText("I have permission to record").click();
  await page
    .getByRole("button", { name: "Create collection session", exact: true })
    .click();
  await expect(page.getByText("SESSION SAVED", { exact: true })).toBeVisible();
}
test("browser motion: synthetic event transport, real normalization and metadata", async ({
  page,
}) => {
  await page.addInitScript(() => {
    // Isolate the declared injected fixture from Chromium's initial trusted all-null device event.
    window.addEventListener(
      "devicemotion",
      (e) => {
        if (e.isTrusted) e.stopImmediatePropagation();
      },
      true,
    );
    Object.defineProperty(DeviceMotionEvent, "requestPermission", {
      value: async () => "granted",
      configurable: true,
    });
  });
  await createCollection(page);
  await page
    .getByLabel("Motion source provenance", { exact: true })
    .selectOption("synthetic");
  await page
    .getByRole("button", { name: "Start motion capture", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Stop motion", exact: true }),
  ).toBeVisible();
  await page.evaluate(() => {
    for (let i = 0; i < 401; i++) {
      const e = new DeviceMotionEvent("devicemotion", {
        acceleration: { x: 0, y: 0, z: 0 },
        accelerationIncludingGravity: { x: 0, y: 0, z: 9.8 },
        rotationRate: {
          beta: 5 + 300 * Math.exp(-1 * ((i - 200) / 10) ** 2),
          gamma: 0,
          alpha: 0,
        },
      });
      Object.defineProperty(e, "timeStamp", { value: 1000 + i * 10 });
      window.dispatchEvent(e);
    }
  });
  await expect(page.getByText("401", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: /Mark operator cue/ }).click();
  await page.evaluate(() => {
    Object.defineProperty(document, "hidden", {
      configurable: true,
      value: true,
    });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await expect(
    page.getByRole("status").filter({ hasText: "Page hidden / screen locked" }),
  ).toBeVisible();
  await page.evaluate(() => {
    Object.defineProperty(document, "hidden", {
      configurable: true,
      value: false,
    });
  });
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export raw CSV + metadata" }).click();
  expect((await download).suggestedFilename()).toBe("motion.csv");
  await page
    .getByRole("button", { name: "Save motion to session", exact: true })
    .click();
  await expect(
    page.getByText("browser-motion.csv", { exact: true }),
  ).toHaveCount(2);
  await expect(page.getByText("ready", { exact: true })).toHaveCount(2); // import card and quality panel
  await page.getByRole("link", { name: "Open replay", exact: true }).click();
  await expect(page).toHaveURL(/\/sessions\/[a-f0-9-]+$/);
  const sid = new URL(page.url()).pathname.split("/").at(-1)!;
  const detail = await (
    await page.request.get(`/api/v1/sessions/${sid}`)
  ).json();
  expect(detail.dataset_kind).toBe("synthetic");
  expect(detail.sensors[0].samples).toBe(401);
  expect(detail.sensors[0].mapping.capture).toMatchObject({
    source: "browser_devicemotion",
    source_rotation_unit: "deg/s",
    original_first_timestamp_ms: 1000,
    sample_count: 401,
    stop_reason: "Page hidden / screen locked; recording interrupted",
  });
  await page.getByRole("button", { name: "Run baseline", exact: true }).click();
  await expect(page.getByRole("button", { name: /Gyro peak/ })).toHaveCount(1);
  await page.getByLabel("Signal zoom window").selectOption("2000000");
  await page
    .getByRole("button", { name: "Step forward 100 milliseconds" })
    .click();
  await expect(page.getByTestId("playback-time")).toContainText("00:00.10");
  await page.reload();
  await expect(page.getByLabel("Signal zoom window")).toHaveValue("2000000");
  test.info().annotations.push({
    type: "capture-verification-scope",
    description:
      "Injected synthetic DeviceMotion events; actual UI, CSV transport, PostgreSQL, worker normalization and detector. No physical hardware.",
  });
});
test("motion permission denied and unsupported API expose actionable fallback", async ({
  page,
}) => {
  await page.addInitScript(() => {
    Object.defineProperty(DeviceMotionEvent, "requestPermission", {
      value: async () => "denied",
      configurable: true,
    });
  });
  await createCollection(page);
  await page
    .getByRole("button", { name: "Start motion capture", exact: true })
    .click();
  await expect(
    page.getByRole("alert").filter({ hasText: "Motion permission denied" }),
  ).toBeVisible();
  await page.evaluate(() => {
    Object.defineProperty(window, "DeviceMotionEvent", {
      value: undefined,
      configurable: true,
    });
  });
  await page
    .getByRole("button", { name: "Start motion capture", exact: true })
    .click();
  await expect(
    page.getByRole("alert").filter({ hasText: "no DeviceMotion API" }),
  ).toBeVisible();
});
test("browser camera encodes a synthetic device clip and real worker validates it", async () => {
  const browser = await chromium.launch({
    args: [
      "--use-fake-device-for-media-stream",
      "--use-fake-ui-for-media-stream",
    ],
  });
  const context = await browser.newContext({
    baseURL: process.env.TEST_BASE_URL || "http://127.0.0.1:3000",
    permissions: ["camera"],
  });
  const page = await context.newPage();
  try {
    await createCollection(page);
    await page
      .getByLabel("Camera source provenance", { exact: true })
      .selectOption("synthetic");
    await page
      .getByRole("button", { name: "Start camera recording", exact: true })
      .click();
    await expect(
      page.getByRole("button", { name: "Stop camera", exact: true }),
    ).toBeVisible();
    await page.waitForTimeout(2200); // Actual MediaRecorder needs elapsed frames, not a mocked completion.
    await page
      .getByRole("button", { name: "Stop camera", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Save video to session", exact: true })
      .click();
    await expect(page.getByText("camera.webm", { exact: true })).toHaveCount(2);
    await expect(page.getByText("ready", { exact: true })).toHaveCount(2);
    const fixture = fs
      .readFileSync("../../data/fixtures/synthetic-imu.csv", "utf8")
      .split("\n")
      .slice(0, 202)
      .join("\n");
    await page.getByLabel("Sensor CSV file").setInputFiles({
      name: "synthetic-pairing-transport.csv",
      mimeType: "text/csv",
      buffer: Buffer.from(fixture),
    });
    await page.getByLabel("Measurement origin").selectOption("synthetic");
    await page
      .getByRole("button", { name: "Import and normalize", exact: true })
      .click();
    await expect(page.getByText("ready", { exact: true })).toHaveCount(4);
    await page
      .getByLabel("Start cue · sensor seconds", { exact: true })
      .fill("0.1");
    await page
      .getByLabel("Start cue · video seconds", { exact: true })
      .fill("0.2");
    await page
      .getByLabel("End cue · sensor seconds (optional)", { exact: true })
      .fill("1.7");
    await page
      .getByLabel("End cue · video seconds (optional)", { exact: true })
      .fill("1.9");
    await page
      .getByLabel("Pairing / timing evidence", { exact: true })
      .fill(
        "Synthetic transport fixture only; not a physically paired recording",
      );
    await page
      .getByRole("button", { name: "Save alignment revision", exact: true })
      .click();
    await expect(page.getByText("ALIGNMENT R2", { exact: true })).toBeVisible();
    await page.getByRole("link", { name: "Open replay", exact: true }).click();
    await expect(page).toHaveURL(/\/sessions\/[a-f0-9-]+$/);
    const sid = new URL(page.url()).pathname.split("/").at(-1)!;
    const data = await (
      await page.request.get(`/api/v1/sessions/${sid}`)
    ).json();
    expect(data.videos[0].metadata_json.capture.source).toBe("browser_camera");
    expect(data.videos[0].duration_us).toBeGreaterThan(1e6);
    expect(data.dataset_kind).toBe("synthetic");
    expect(data.syncs.at(-1).evidence).toMatchObject({
      paired: false,
      end_residual_us: 100000,
      drift_corrected: false,
    });
    fs.writeFileSync(
      `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/step4-camera-verification.json`,
      JSON.stringify(
        {
          session_id: sid,
          video: data.videos[0],
          scope:
            "Chromium synthetic camera; real MediaRecorder and FFprobe; no physical camera verification",
        },
        null,
        2,
      ),
    );
  } finally {
    await browser.close();
  }
});
