import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { clampTime, nearestFrame, percent, validateDataset } from "./data";
import { lineSegments } from "./visuals";

const dataset = validateDataset(
  JSON.parse(
    readFileSync(
      new URL("../public/data/showcase.json", import.meta.url),
      "utf8",
    ),
  ),
);
const approved = JSON.parse(
  readFileSync(
    new URL(
      "../../../docs/evidence/step6_6/demo-fixtures.json",
      import.meta.url,
    ),
    "utf8",
  ),
);
describe("stored scientific evidence", () => {
  it("retains exactly the reviewed evaluations and the explicit failed experiment", () => {
    for (const expected of approved.curated_experiments) {
      const actual = dataset.experiments.find((e) => e.id === expected.id)!;
      expect(actual.status).toBe(expected.status);
      expect(actual.result.evaluation ?? null).toEqual(expected.evaluation);
      expect(actual.result.events?.length ?? 0).toBe(expected.events);
    }
    expect(
      dataset.experiments.filter((e) => e.status === "failed"),
    ).toHaveLength(1);
    expect(
      dataset.experiments.filter(
        (e) => !e.result.evaluation && e.status === "succeeded",
      ),
    ).toHaveLength(3);
  });
  it("keeps synthetic/non-independent/analytical provenance explicit", () => {
    expect(dataset.dataset_kind).toBe("synthetic");
    expect(dataset.reference.manifest.independent).toBe(false);
    expect(dataset.pose.config.provenance).toBe(
      "generated_analytical_landmarks",
    );
    expect(dataset.sensor.samples).toHaveLength(801);
    expect(dataset.pose.frames).toHaveLength(241);
  });
  it("does not replace undefined precision with zero", () => {
    const offset = dataset.experiments.find((e) =>
      e.name.startsWith("Offset"),
    )!;
    expect(offset.result.evaluation!.precision).toBeNull();
    expect(percent(offset.result.evaluation!.precision)).toBe("—");
    expect(percent(offset.result.evaluation!.recall)).toBe("0.0%");
  });
  it("rejects incorrectly labeled or incomplete snapshots", () => {
    expect(() =>
      validateDataset({ ...dataset, dataset_kind: "recorded" }),
    ).toThrow();
    expect(() =>
      validateDataset({
        ...dataset,
        reference: { manifest: { independent: true } },
      }),
    ).toThrow();
    expect(() => validateDataset({ ...dataset, experiments: [] })).toThrow();
  });
});
describe("replay and truthful visualization", () => {
  it("selects the closest stored timestamp, not an interpolated prediction", () => {
    const frame = nearestFrame(dataset.pose.frames, 2010000);
    expect(frame.t_video_us).toBe(2000000);
    expect(dataset.pose.frames.includes(frame)).toBe(true);
    expect(nearestFrame(dataset.pose.frames, -1)).toBe(dataset.pose.frames[0]);
    expect(nearestFrame(dataset.pose.frames, 9e6)).toBe(
      dataset.pose.frames.at(-1),
    );
  });
  it("bounds seeking and invalid deep-link time", () => {
    expect(clampTime(-10, 8e6)).toBe(0);
    expect(clampTime(9e6, 8e6)).toBe(8e6);
    expect(clampTime(Number.NaN, 8e6)).toBe(0);
  });
  it("does not bridge missing measurements in chart lines", () => {
    const p = [
      { t_session_us: 0, value: 1 },
      { t_session_us: 10000, value: 2 },
      { t_session_us: 1500000, value: 3 },
      { t_session_us: 1510000, value: 4 },
    ];
    expect(lineSegments(p, 0, 2e6, 900, 150).segments).toHaveLength(2);
    expect(
      lineSegments(
        [
          { t_session_us: 0, value: 1 },
          { t_session_us: 10000, value: null },
          { t_session_us: 20000, value: 2 },
        ],
        0,
        30000,
        900,
        150,
      ).segments,
    ).toHaveLength(2);
  });
});
