import { describe, expect, it } from "vitest";
import { MotionBuffer, type MotionObservation } from "./motion";
const event = (timeStamp: number): MotionObservation => ({
  timeStamp,
  acceleration: { x: 1, y: null, z: 3 },
  accelerationIncludingGravity: { x: 4, y: 5, z: 9.8 },
  rotationRate: { beta: 180, gamma: 90, alpha: null },
});
describe("measured browser motion normalization", () => {
  it("uses beta/x and gamma/y, converts degrees, retains missing channels and raw time", () => {
    const b = new MotionBuffer("linear");
    b.append(event(1234));
    b.append(event(1254));
    expect(b.rows[0]).toMatchObject({
      t_us: 0,
      event_timestamp_ms: 1234,
      ax: 1,
      ay: null,
      gx: Math.PI,
      gy: Math.PI / 2,
      gz: null,
    });
    expect(b.summary()).toMatchObject({
      count: 2,
      hz: 50,
      acceleration: 0,
      gyroscope: 0,
    });
    expect(b.csv()).toContain("0,1234,1,,3,");
  });
  it("does not substitute gravity acceleration and rejects nonmonotonic timestamps", () => {
    const b = new MotionBuffer("including_gravity");
    b.append(event(20));
    b.append(event(20));
    b.append(event(19));
    b.append(event(40));
    expect(b.rows[0].az).toBe(9.8);
    expect(b.discarded).toBe(2);
    expect(b.rows[1].t_us).toBe(20_000);
    const a = new MotionBuffer("linear");
    a.append({ ...event(0), acceleration: null });
    expect(a.rows[0].az).toBeNull();
  });
});
