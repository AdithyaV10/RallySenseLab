import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";

const headers = { "x-lab-client": "rallysense" };
for (const kind of ["csv", "video"] as const) {
  test(`advertised ${kind} upload accepts an intact body above 10 MiB`, async ({
    request,
  }) => {
    const created = await request.post("/api/v1/sessions", {
      headers,
      data: {
        title: `Disposable audit ${kind} upload`,
        dataset_kind: "synthetic",
      },
    });
    expect(created.status()).toBe(201);
    const sid = (await created.json()).id;
    try {
      let buffer: Buffer;
      if (kind === "csv") {
        buffer = Buffer.from(
          "timestamp_s,ax_m_s2,ay_m_s2,az_m_s2,gx_rad_s,gy_rad_s,gz_rad_s\n" +
            Array.from(
              { length: 450001 },
              (_, i) => `${(i / 1000).toFixed(3)},0,0,9.80665,0,0,0\n`,
            ).join(""),
        );
      } else {
        // One-second FFmpeg synthetic MP4 plus a legal padding box; no private recording.
        const original = fs.readFileSync(
          path.resolve("../../storage/step5-small.mp4"),
        );
        const padding = Buffer.alloc(12 * 1024 * 1024);
        padding.writeUInt32BE(padding.length, 0);
        padding.write("free", 4, "ascii");
        buffer = Buffer.concat([original, padding]);
      }
      const route = `/api/v1/sessions/${sid}/${kind === "csv" ? "sensor-imports" : "videos"}`;
      const multipart = {
        file: {
          name: kind === "csv" ? "audit.csv" : "audit.mp4",
          mimeType: kind === "csv" ? "text/csv" : "video/mp4",
          buffer,
        },
        [kind === "csv" ? "mapping" : "metadata"]: JSON.stringify({
          provenance: "synthetic",
        }),
      };
      const direct = await request.post(`http://127.0.0.1:8000${route}`, {
        headers: {
          "x-lab-token":
            process.env.LOCAL_TOKEN || "rallysense-local-development",
        },
        multipart,
      });
      expect(direct.status(), await direct.text()).toBe(202);
      const directJob = await direct.json();
      await expect
        .poll(
          async () =>
            (await (await request.get(`/api/v1/jobs/${directJob.id}`)).json())
              .state,
          { timeout: 90000 },
        )
        .toBe("succeeded");
      const response = await request.post(route, {
        headers,
        multipart,
      });
      test.info().annotations.push({
        type: "actual-upload-comparison",
        description: JSON.stringify({
          bytes: buffer.length,
          sha256: createHash("sha256").update(buffer).digest("hex"),
          direct_status: direct.status(),
          direct_job: "succeeded",
          proxy_status: response.status(),
        }),
      });
      expect(response.status(), await response.text()).toBe(202);
      const job = await response.json();
      await expect
        .poll(
          async () =>
            (await (await request.get(`/api/v1/jobs/${job.id}`)).json()).state,
          { timeout: 90000 },
        )
        .toBe("succeeded");
    } finally {
      // Delete only the fixture created by this test.
      expect(
        (await request.delete(`/api/v1/sessions/${sid}`, { headers })).status(),
      ).toBe(202);
    }
  });
}
