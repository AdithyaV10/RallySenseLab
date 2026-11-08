import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

test("alignment revisions immediately refetch positive, negative, partial and empty windows", async ({
  page,
  request,
}) => {
  const headers = { "x-lab-client": "rallysense" };
  const created = await request.post("/api/v1/sessions", {
    headers,
    data: {
      title: "Disposable alignment regression",
      dataset_kind: "synthetic",
    },
  });
  expect(created.status()).toBe(201);
  const sid = (await created.json()).id;
  try {
    const upload = await request.post(
      `/api/v1/sessions/${sid}/sensor-imports`,
      {
        headers,
        multipart: {
          file: {
            name: "fixture.csv",
            mimeType: "text/csv",
            buffer: fs.readFileSync(
              path.resolve("../../data/fixtures/synthetic-imu.csv"),
            ),
          },
          mapping: JSON.stringify({ provenance: "synthetic" }),
        },
      },
    );
    const job = await upload.json();
    await expect
      .poll(
        async () =>
          (await (await request.get(`/api/v1/jobs/${job.id}`)).json()).state,
      )
      .toBe("succeeded");
    await page.goto(`/sessions/${sid}`);
    await page.getByLabel("Signal zoom window").selectOption("2000000");
    await page.getByLabel("Session timeline").fill("4000000");
    await page.waitForLoadState("networkidle");
    const observations = [];
    for (const [offset, start, end] of [
      [1, 3000000, 5000000],
      [-1, 5000000, 7000000],
      [5, 0, 1000000],
      [10, null, null],
    ]) {
      const samples: string[] = [];
      const listen = (r: { url(): string }) => {
        if (r.url().includes("/samples?")) samples.push(r.url());
      };
      page.on("request", listen);
      await page.getByLabel("Sensor offset in seconds").fill(String(offset));
      const saved = page.waitForResponse(
        (r) => r.url().endsWith("/sync-configurations") && r.status() === 201,
      );
      await page
        .getByRole("button", { name: "Save alignment", exact: true })
        .click();
      await saved;
      if (start !== null)
        await expect
          .poll(() =>
            samples.some((u) => u.includes(`start_us=${start}&end_us=${end}`)),
          )
          .toBe(true);
      await page.waitForLoadState("networkidle");
      if (start === null) expect(samples).toEqual([]);
      observations.push({ offset, requests: samples });
      page.off("request", listen);
    }
    test
      .info()
      .annotations.push({
        type: "alignment-window-regression",
        description: JSON.stringify(observations),
      });
  } finally {
    expect(
      (await request.delete(`/api/v1/sessions/${sid}`, { headers })).status(),
    ).toBe(202);
  }
});
