import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { afterEach } from "vitest";
import { modeUnavailable, percent, Experiment } from "./types";
import { ResultComparison } from "./results";
afterEach(cleanup);

const experiment = (id: string, scored = false): Experiment => ({
  id,
  session_id: "session",
  created_at: "2026-11-03T00:00:00Z",
  name: `Fixture ${id}`,
  status: "succeeded",
  fingerprint: "hash",
  error: null,
  reused_from_id: null,
  manifest: {
    algorithm: "imu_motion_window@1.0.0",
    session: { dataset_kind: "synthetic" },
    request: {
      mode: "imu",
      start_us: 0,
      end_us: 8e6,
      tolerance_us: 150000,
      comparison: "synthetic_fixture",
    },
  },
  result: {
    events: [
      {
        t_session_us: 2e6,
        event_type: "gyro_peak_v1",
        magnitude: 6,
        prominence: 5,
      },
    ],
    score_kind: "rad/s",
    quality: {},
    components: {},
    eligible_intervals: [],
    signal: [],
    limitations: [],
    references: [],
    corruption: {},
    processing_ms: 5,
    evaluation_note: "Synthetic software verification, not real-world accuracy",
    evaluation: scored
      ? {
          evaluator: "test",
          tolerance_us: 150000,
          tp: 1,
          fp: 0,
          fn: 1,
          precision: 1,
          recall: 0.5,
          f1: 2 / 3,
          mean_absolute_error_us: 10000,
          median_absolute_error_us: 10000,
          mean_signed_error_us: 10000,
          false_positives_per_minute: 0,
          matches: [],
          unmatched_predictions: [],
          missed_references: [],
          undefined_rule: "Explicit denominators",
        }
      : null,
  },
});

describe("research evidence presentation", () => {
  it("rejects unavailable modalities and unrelated mixed fusion", () => {
    expect(modeUnavailable("video", true, false, "synthetic")).toMatch(/pose/);
    expect(modeUnavailable("fusion", true, true, "mixed")).toMatch(
      /not physically paired/,
    );
    expect(modeUnavailable("fusion", true, true, "recorded")).toBe("");
  });
  it("does not invent accuracy without labels and seeks real predictions", () => {
    const seek = vi.fn();
    render(<ResultComparison runs={[experiment("a")]} onSeek={seek} />);
    expect(screen.getByText("Accuracy unavailable")).toBeTruthy();
    expect(screen.queryByText("PRECISION")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /Inspect imu event/ }));
    expect(seek).toHaveBeenCalledWith(2e6);
    expect(screen.getByText(/Synthetic software verification/)).toBeTruthy();
  });
  it("renders stored metrics and warns on unequal evaluation protocols", () => {
    const a = experiment("a", true),
      b = experiment("b", true);
    a.manifest = { ...a.manifest, sync: { id: "original" } };
    b.manifest = { ...b.manifest, sync: { id: "different" } };
    render(<ResultComparison runs={[a, b]} onSeek={() => {}} />);
    expect(screen.getAllByText("66.7%")).toHaveLength(2);
    expect(screen.getByText(/do not isolate algorithm effects/)).toBeTruthy();
    expect(percent(null)).toBe("—");
  });
});
