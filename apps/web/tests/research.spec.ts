import { test, expect } from "@playwright/test";

test("paired synthetic research: freeze labels, three modes, corruption, comparison, export and replay", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const response = await request.post("/api/v1/research-demo-sessions", {
    headers: { "x-lab-client": "rallysense" },
  });
  expect(response.ok()).toBeTruthy();
  const demo = await response.json();
  await expect
    .poll(
      async () => {
        const d = await (
          await request.get(`/api/v1/sessions/${demo.id}`)
        ).json();
        return d.poses?.filter((p: { status: string }) => p.status === "ready")
          .length;
      },
      { timeout: 45000 },
    )
    .toBe(1);
  await page.goto(`/sessions/${demo.id}?tab=research`);
  await expect(
    page.getByRole("heading", { name: /Three perspectives/ }),
  ).toBeVisible();
  await expect(
    page.getByText("Generated signals test software, not tennis performance."),
  ).toBeVisible();
  await page.getByText("Reference laboratory", { exact: true }).click();
  await page.getByLabel("Annotation set").selectOption({
    label: "Generated paired pulse centers · revision 1 · synthetic",
  });
  await page
    .getByLabel("Operational definition")
    .fill(
      "Analytical Gaussian pulse center on the shared generated fixture clock.",
    );
  await page
    .getByLabel("Labeling procedure")
    .fill(
      "Programmatic generator markers, not independent human labels or tennis ground truth.",
    );
  const frozenResponse = page.waitForResponse(
    (r) => r.url().endsWith("/freeze") && r.status() === 201,
  );
  await page.getByRole("button", { name: "Freeze reference revision" }).click();
  const frozen = await (await frozenResponse).json();
  await page
    .getByLabel("Frozen reference", { exact: true })
    .selectOption(frozen.id);
  const suffix = Date.now();
  async function run(name: string) {
    await page.getByLabel("Experiment name").fill(`${name} ${suffix}`);
    const created = page.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        r.url().endsWith("/experiments") &&
        r.status() === 202,
    );
    await page
      .getByRole("button", { name: "Run experiment", exact: true })
      .click();
    const exp = await (await created).json();
    await expect
      .poll(
        async () =>
          (await (await request.get(`/api/v1/experiments/${exp.id}`)).json())
            .status,
      )
      .toBe("succeeded");
    await expect(
      page
        .getByTestId("experiment-result")
        .filter({
          has: page.getByRole("heading", {
            name: `${name} ${suffix}`,
            exact: true,
          }),
        }),
    ).toContainText("succeeded");
    return await (await request.get(`/api/v1/experiments/${exp.id}`)).json();
  }
  const imu = await run("IMU clean");
  expect(imu.result.events).toHaveLength(2);
  expect(imu.result.evaluation).toMatchObject({ tp: 2, fp: 0, fn: 0, f1: 1 });
  await page.getByRole("button", { name: /A \/ VISUAL.*Video only/ }).click();
  const video = await run("Video clean");
  expect(video.result.events).toHaveLength(2);
  expect(video.result.evaluation.tp).toBe(2);
  await page
    .getByRole("button", { name: /C \/ ASSOCIATION.*Multimodal fusion/ })
    .click();
  await page.getByLabel(/These modalities observe/).check();
  await page
    .getByLabel("Alignment evidence")
    .fill(
      "Analytical shared clock from generated paired inputs; no physical tennis recording.",
    );
  const fusion = await run("Fusion clean");
  expect(fusion.result.events).toHaveLength(2);
  expect(fusion.result.events[0].video_time_us).toBeGreaterThan(0);
  await expect(page.getByTestId("experiment-result")).toHaveCount(3);
  await page.screenshot({
    path: `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/research-comparison.png`,
    fullPage: true,
  });
  await page.getByLabel("Artificial condition").selectOption("sync");
  await page.getByLabel("Corruption severity").fill("1");
  const degraded = await run("Fusion offset +1s");
  expect(degraded.result.events).toHaveLength(0);
  expect(degraded.result.evaluation).toMatchObject({
    tp: 0,
    fp: 0,
    fn: 2,
    f1: 0,
  });
  expect(
    (await (await request.get(`/api/v1/experiments/${fusion.id}`)).json())
      .result.events,
  ).toHaveLength(2);
  await page.screenshot({
    path: `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/research-robustness.png`,
    fullPage: true,
  });
  const exported = await request.get(
    `/api/v1/experiments/${degraded.id}/report`,
  );
  expect(exported.ok()).toBeTruthy();
  expect(await exported.text()).toContain('"fn": 2');
  const reportPage = await page.context().newPage();
  await reportPage.goto(`/experiments/${degraded.id}/report`);
  await expect(
    reportPage.getByRole("heading", { name: degraded.name, exact: true }),
  ).toBeVisible();
  await expect(reportPage.getByText(/TP 0 · FP 0 · FN 2/)).toBeVisible();
  await reportPage.emulateMedia({ media: "print" });
  await expect(
    reportPage.getByRole("button", { name: "Print / Save PDF" }),
  ).toBeHidden();
  await reportPage.pdf({
    path: `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/step4-synthetic-report.pdf`,
    format: "A4",
    printBackground: true,
  });
  await reportPage.close();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: `${process.env.TEST_EVIDENCE_DIRECTORY || "../../docs/evidence"}/research-mobile.png`,
    fullPage: true,
  });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page
    .getByRole("button", { name: /Inspect fusion event/ })
    .first()
    .click();
  await expect(page.getByTestId("playback-time")).toContainText("00:02.00");
  await expect(
    page.getByLabel("Generated fixture landmark overlay"),
  ).toBeVisible();
  await expect(
    page.getByText(/Generated fixture landmarks \(not MediaPipe\)/),
  ).toBeVisible();
  expect(errors).toEqual([]);
  test.info().annotations.push({
    type: "actual-research-results",
    description: JSON.stringify({
      session: demo.id,
      imu: imu.id,
      video: video.id,
      fusion: fusion.id,
      degraded: degraded.id,
      clean_fusion_events: 2,
      degraded_fusion_events: 0,
      evidence: "synthetic software verification only",
    }),
  });
});

test("human reference set revisions and inference eligibility are exposed in the UI", async ({
  page,
  request,
}) => {
  const headers = { "x-lab-client": "rallysense" };
  const session = await (
    await request.post("/api/v1/sessions", {
      headers,
      data: { title: "Research label workflow", dataset_kind: "recorded" },
    })
  ).json();
  try {
    await page.goto(`/sessions/${session.id}?tab=research`);
    await expect(
      page.getByRole("button", { name: /B \/ INERTIAL.*IMU only/ }),
    ).toBeDisabled();
    await expect(
      page.getByRole("button", { name: /A \/ VISUAL.*Video only/ }),
    ).toBeDisabled();
    await page.getByText("Reference laboratory", { exact: true }).click();
    await page.getByRole("button", { name: "Create annotation set" }).click();
    await page.getByLabel("Research label time").fill("1.2");
    await page
      .getByLabel("Operational definition")
      .fill("Visible wrist extension at the end of the forward motion.");
    await page
      .getByLabel("Labeling procedure")
      .fill(
        "UI software test only; no real observation or independence claim.",
      );
    const added = page.waitForResponse(
      (r) => r.url().includes("/annotations?") && r.status() === 201,
    );
    await page.getByRole("button", { name: "Add research label" }).click();
    await added;
    const freeze = page.waitForResponse(
      (r) => r.url().endsWith("/freeze") && r.status() === 201,
    );
    await page
      .getByRole("button", { name: "Freeze reference revision" })
      .click();
    const ref = await (await freeze).json();
    expect(ref.manifest.independent).toBe(false);
    expect(ref.events[0].t_session_us).toBe(1_200_000);
    await page
      .getByLabel("Frozen reference", { exact: true })
      .selectOption(ref.id);
    await expect(page.getByLabel("Comparison semantics")).toBeVisible();
  } finally {
    await request.delete(`/api/v1/sessions/${session.id}`, { headers });
  }
});
