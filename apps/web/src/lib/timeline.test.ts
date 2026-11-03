import { describe, it, expect } from "vitest";
import {
  toSession,
  toSource,
  roundHalfAway,
  nearestFrame,
  containRect,
} from "./timeline";
describe("timeline contracts", () => {
  it("keeps overlay geometry inside portrait and letterboxed video rectangles", () => {
    expect(containRect(1920, 1080, 600, 400)).toEqual({
      width: 600,
      height: 337.5,
    });
    expect(containRect(1080, 1920, 600, 400)).toEqual({
      width: 225,
      height: 400,
    });
  });
  it("maps both directions with the documented positive offset", () => {
    expect(toSession(2_000_000, 1_500_000)).toBe(3_500_000);
    expect(toSource(5_000_000, 1_500_000)).toBe(3_500_000);
  });
  it("rounds signed ties identically to Python", () => {
    expect(roundHalfAway(-0.5)).toBe(-1);
    expect(roundHalfAway(0.5)).toBe(1);
  });
  it("finds a nearby frame and hides stale observations", () => {
    const frames = [
      { t_video_us: 0 },
      { t_video_us: 100000 },
      { t_video_us: 1000000 },
    ];
    expect(nearestFrame(frames, 140000)?.t_video_us).toBe(100000);
    expect(nearestFrame(frames, 500000)).toBeNull();
    expect(nearestFrame([], 0)).toBeNull();
  });
});
