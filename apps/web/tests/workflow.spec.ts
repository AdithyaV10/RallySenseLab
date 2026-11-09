import { test, expect } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

test("synthetic session: computed events, seek, label edits, saved sync and reload", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Understand/ })).toBeVisible();
  await page.screenshot({
    path: `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/landing-desktop.png`,
    fullPage: true,
  });
  await page.getByRole("button", { name: "Explore the demo" }).click();
  await expect(
    page.getByRole("heading", { name: "Baseline / synthetic motion" }),
  ).toBeVisible();
  // Mutate a newly created label set, never a pre-existing workspace reference set.
  const sid = new URL(page.url()).pathname.split("/").at(-1)!;
  const isolated = await request.post(`/api/v1/sessions/${sid}/annotation-sets`, {
    headers: { "x-lab-client": "rallysense" },
    data: { name: `Browser-only observations ${Date.now()}` },
  });
  expect(isolated.status()).toBe(201);
  const labelSetId = (await isolated.json()).id;
  await page.reload();
  await page.getByLabel("Replay reference set").selectOption(labelSetId);
  await expect(page.getByRole("button", { name: /Gyro peak/ })).toHaveCount(5, {
    timeout: 30000,
  });
  await page
    .getByRole("button", { name: /Gyro peak/ })
    .first()
    .click();
  await expect(page.getByTestId("playback-time")).toContainText("00:02.20");
  await page.getByTestId("gyro-chart").scrollIntoViewIfNeeded();
  const graph = await page.getByTestId("gyro-chart").boundingBox();
  await page.mouse.click(graph!.x + graph!.width * 0.5, graph!.y + 55);
  await expect
    .poll(async () =>
      Number(await page.getByLabel("Session timeline").inputValue()),
    )
    .toBeGreaterThan(7_000_000);
  await page.getByLabel("Blinded labels").check();
  await expect(page.getByTestId("gyro-chart")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Next signal event" }),
  ).toBeDisabled();
  await page.getByLabel("Blinded labels").uncheck();
  await page
    .getByRole("button", { name: /Gyro peak/ })
    .first()
    .click();
  await page.getByLabel("Reference note").fill("E2E independent observation");
  await page.getByRole("button", { name: "Add marker at cursor" }).click();
  await expect(
    page.getByText("E2E independent observation", { exact: false }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Edit reference", exact: true })
    .last()
    .click();
  await page.getByLabel("Reference time in seconds").fill("2.3");
  await page.getByRole("button", { name: "Save reference edit" }).click();
  await page.getByLabel("Sensor offset in seconds").fill("0.25");
  await page
    .getByRole("button", { name: "Save alignment", exact: true })
    .click();
  await expect(page.getByText(/earlier alignment/)).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Sensor offset in seconds")).toHaveValue("0.25");
  await page.getByLabel("Replay reference set").selectOption(labelSetId);
  await page.getByRole("button", { name: /References/ }).click();
  await expect(page.getByText(/E2E independent observation/)).toBeVisible();
  await page
    .getByRole("button", { name: "Delete reference", exact: true })
    .last()
    .click();
  await page.getByLabel("Sensor offset in seconds").fill("0");
  await page
    .getByRole("button", { name: "Save alignment", exact: true })
    .click();
  await page.getByRole("button", { name: "Run baseline" }).click();
  await page.getByRole("button", { name: /Signal events/ }).click();
  await expect(page.getByRole("button", { name: /Gyro peak/ })).toHaveCount(5);
  await page.screenshot({
    path: `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/replay-desktop.png`,
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/replay-mobile.png`,
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});

test("session creation, CSV mapping import, inference and deletion through the UI", async ({
  page,
}) => {
  await page.goto("/sessions");
  await page.getByRole("button", { name: "New session", exact: true }).click();
  const title = `Browser integration ${Date.now()}`;
  await page.getByPlaceholder("e.g. Forehand practice / 01").fill(title);
  await page.getByLabel("Dataset origin").selectOption("synthetic");
  await page
    .getByRole("button", { name: "Create session", exact: true })
    .click();
  await expect(page.getByRole("heading", { name: title })).toBeVisible();
  await page
    .getByLabel("Sensor CSV file")
    .setInputFiles(path.resolve("../../data/fixtures/synthetic-imu.csv"));
  await page.getByRole("button", { name: "Import and normalize" }).click();
  await expect(page.getByText("ready", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Synchronized replay" }).click();
  await page.getByRole("button", { name: "Run baseline" }).click();
  await expect(page.getByRole("button", { name: /Gyro peak/ })).toHaveCount(5);
  await page.goto("/sessions");
  await page
    .getByRole("button", { name: `Delete ${title}`, exact: true })
    .click();
  await page.getByRole("button", { name: "Delete session and data" }).click();
  await expect(page.getByRole("heading", { name: title })).toHaveCount(0);
});

test("real MediaPipe package processes uploaded official demonstration video", async ({
  page,
}) => {
  const clip = path.resolve("../../data/private/pose-sample.mp4");
  test.skip(
    !fs.existsSync(clip),
    "Optional external official clip not present; see TESTING.md for acquisition",
  );
  const logs: string[] = [];
  page.on("console", (m) => {
    if (m.type() === "error") logs.push(m.text());
  });
  await page.goto("/sessions");
  await page.getByRole("button", { name: "New session", exact: true }).click();
  await page
    .getByPlaceholder("e.g. Forehand practice / 01")
    .fill(`Pose smoke ${Date.now()}`);
  await page.getByLabel("Dataset origin").selectOption("mixed");
  await page
    .getByRole("button", { name: "Create session", exact: true })
    .click();
  await page.getByLabel("Video file").setInputFiles(clip);
  await expect(page.getByText("ready", { exact: true })).toBeVisible();
  const fixture = fs
    .readFileSync(path.resolve("../../data/fixtures/synthetic-imu.csv"), "utf8")
    .split("\n")
    .slice(0, 402)
    .join("\n");
  await page.getByLabel("Sensor CSV file").setInputFiles({
    name: "synthetic-short.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(fixture),
  });
  await page.getByLabel("Measurement origin").selectOption("synthetic");
  await page.getByRole("button", { name: "Import and normalize" }).click();
  await expect(page.getByText("ready", { exact: true })).toHaveCount(2);
  await page.getByRole("button", { name: "Synchronized replay" }).click();
  await page.getByLabel("Pose sampling target").selectOption("30");
  await page.getByRole("button", { name: "Extract pose", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Complete", {
    timeout: 110000,
  });
  await expect(page.getByText(/MediaPipe · \d+ sampled frames/)).toBeVisible();
  await page.getByLabel("Session timeline").fill("1000000");
  await expect(page.getByLabel("MediaPipe pose overlay")).toBeVisible();
  await page.getByLabel("Sensor offset in seconds").fill("0.1");
  await page
    .getByRole("button", { name: "Save alignment", exact: true })
    .click();
  await page.getByRole("button", { name: "Run baseline" }).click();
  await expect(page.getByRole("button", { name: /Gyro peak/ })).toHaveCount(1);
  await page.getByRole("button", { name: /Gyro peak/ }).click();
  await expect
    .poll(() =>
      page
        .locator(".video-fit video")
        .evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBeCloseTo(2.3, 1);
  const replayVideo = page.locator(".video-fit video");
  await expect
    .poll(() =>
      replayVideo.evaluate((v: HTMLVideoElement) => v.error?.message || null),
    )
    .toBeNull();
  await page
    .getByRole("button", { name: "Play playback", exact: true })
    .click();
  await expect
    .poll(() => replayVideo.evaluate((v: HTMLVideoElement) => v.currentTime))
    .toBeGreaterThan(2.6);
  await page
    .getByRole("button", { name: "Pause playback", exact: true })
    .click();
  // Next.js also owns an empty route-announcer alert; assert actual media state.
  await expect(page.locator(".media-stage .error-box")).toHaveCount(0);
  await expect
    .poll(() =>
      replayVideo.evaluate((v: HTMLVideoElement) => v.error?.message || null),
    )
    .toBeNull();
  await page.screenshot({
    path: `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/pose-extraction.png`,
    fullPage: true,
  });
  const info = await page.getByRole("status").textContent();
  const sampledSessionId = new URL(page.url()).pathname.split("/").at(-1)!;
  const sampledSession = await (
    await page.request.get(`/api/v1/sessions/${sampledSessionId}`)
  ).json();
  const denseTrack = sampledSession.poses.find(
    (p: { status: string; config: { sample_target_hz: number } }) =>
      p.status === "ready" && p.config.sample_target_hz === 30,
  );
  expect(denseTrack.config.playback_rate).toBe(0.5);
  expect(denseTrack.quality.observed_sample_hz).toBeGreaterThan(0);
  test.info().annotations.push({
    type: "measured-dense-pose-cadence",
    description: JSON.stringify({
      track_id: denseTrack.id,
      target_hz: 30,
      quality: denseTrack.quality,
    }),
  });
  test.info().annotations.push({
    type: "actual-pose-execution",
    description: info || "",
  });
  await page
    .getByLabel("Pose sampling method")
    .selectOption("seek_backpressure");
  await page
    .getByRole("button", { name: "Extract new track", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Complete", {
    timeout: 110000,
  });
  const seekSession = await (
    await page.request.get(`/api/v1/sessions/${sampledSessionId}`)
  ).json();
  const seekTrack = seekSession.poses.find(
    (p: { status: string; config: { sampling_method: string } }) =>
      p.status === "ready" && p.config.sampling_method === "seek_backpressure",
  );
  expect(seekTrack.quality.processed_frames).toBeGreaterThan(100);
  expect(seekTrack.quality.max_gap_us).toBeLessThanOrEqual(160000);
  test
    .info()
    .annotations.push({
      type: "measured-seek-pose-cadence",
      description: JSON.stringify({
        track_id: seekTrack.id,
        quality: seekTrack.quality,
        scope: "Actual permitted sample clip; software integration only",
      }),
    });
  await page.getByLabel("Pose sampling method").selectOption("playback");
  await page.route("**/pose-worker.js", (route) =>
    route.fulfill({
      contentType: "application/javascript",
      body: "throw new Error('Forced worker failure for fallback verification')",
    }),
  );
  await page.getByLabel("Pose sampling target").selectOption("10");
  await page
    .getByRole("button", { name: "Extract new track", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Complete", {
    timeout: 110000,
  });
  await expect(page.getByRole("status")).toContainText("main_thread_fallback");
  test.info().annotations.push({
    type: "actual-fallback-execution",
    description: (await page.getByRole("status").textContent()) || "",
  });
  await page
    .getByRole("button", { name: "Sensor Fusion Challenge", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: /C \/ ASSOCIATION.*Multimodal fusion/ }),
  ).toBeDisabled();
  await page.getByRole("button", { name: /A \/ VISUAL.*Video only/ }).click();
  await page
    .getByText("Inputs, timing & algorithm parameters", { exact: true })
    .click();
  await page.getByLabel("Video speed (torso/s)", { exact: true }).fill("0.1");
  await page.getByLabel("Peak prominence", { exact: true }).fill("0.05");
  await page.getByLabel("Adaptive threshold k", { exact: true }).fill("1");
  const experimentResponse = page.waitForResponse(
    (r) =>
      r.url().endsWith("/experiments") &&
      r.request().method() === "POST" &&
      r.status() === 202,
  );
  await page
    .getByRole("button", { name: "Run experiment", exact: true })
    .click();
  const experiment = await (await experimentResponse).json();
  await expect
    .poll(
      async () =>
        (
          await (
            await page.request.get(`/api/v1/experiments/${experiment.id}`)
          ).json()
        ).status,
    )
    .toBe("succeeded");
  const actual = await (
    await page.request.get(`/api/v1/experiments/${experiment.id}`)
  ).json();
  expect(actual.result.events.length).toBeGreaterThan(0);
  expect(actual.result.evaluation).toBeNull();
  test.info().annotations.push({
    type: "actual-stored-pose-inference",
    description: JSON.stringify({
      id: actual.id,
      events: actual.result.events.length,
      evaluation: actual.result.evaluation,
      evidence:
        "Official video integration input; no independent tennis ground truth",
    }),
  });
  await expect(
    page.getByText("Accuracy unavailable", { exact: true }),
  ).toBeVisible();
  expect(
    logs.filter((l) => l.includes("Unhandled") || l.includes("TypeError")),
  ).toEqual([]);
});
