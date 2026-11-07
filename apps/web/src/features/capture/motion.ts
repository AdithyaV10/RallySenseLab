export type AccelerationKind = "linear" | "including_gravity";
type Vector = { x: number | null; y: number | null; z: number | null };
export type MotionObservation = {
  timeStamp: number;
  acceleration: Vector | null;
  accelerationIncludingGravity: Vector | null;
  rotationRate: {
    alpha: number | null;
    beta: number | null;
    gamma: number | null;
  } | null;
};
export type MotionRow = {
  t_us: number;
  event_timestamp_ms: number;
  ax: number | null;
  ay: number | null;
  az: number | null;
  gx: number | null;
  gy: number | null;
  gz: number | null;
  beta_deg_s: number | null;
  gamma_deg_s: number | null;
  alpha_deg_s: number | null;
};
const finite = (v: number | null | undefined) =>
  typeof v === "number" && Number.isFinite(v) ? v : null;
const radians = (v: number | null) => (v === null ? null : (v * Math.PI) / 180);

/** Raw device coordinates. W3C rotation beta=x, gamma=y, alpha=z; no attitude reconstruction. */
export class MotionBuffer {
  rows: MotionRow[] = [];
  firstTimestamp: number | null = null;
  discarded = 0;
  private acceleration = 0;
  private gyroscope = 0;
  private maxGapUs = 0;
  constructor(public kind: AccelerationKind) {}
  append(event: MotionObservation): boolean {
    if (!Number.isFinite(event.timeStamp)) {
      this.discarded++;
      return false;
    }
    if (this.rows.length >= 120_000) return false;
    const origin = this.firstTimestamp ?? event.timeStamp;
    const t_us = Math.round((event.timeStamp - origin) * 1000);
    if (
      t_us < 0 ||
      (this.rows.length > 0 && t_us <= this.rows[this.rows.length - 1].t_us)
    ) {
      this.discarded++;
      return false;
    }
    if (t_us > 1_200_000_000) return false;
    this.firstTimestamp = origin;
    const a =
      this.kind === "linear"
        ? event.acceleration
        : event.accelerationIncludingGravity;
    const r = event.rotationRate;
    const beta = finite(r?.beta),
      gamma = finite(r?.gamma),
      alpha = finite(r?.alpha);
    const row: MotionRow = {
      t_us,
      event_timestamp_ms: event.timeStamp,
      ax: finite(a?.x),
      ay: finite(a?.y),
      az: finite(a?.z),
      gx: radians(beta),
      gy: radians(gamma),
      gz: radians(alpha),
      beta_deg_s: beta,
      gamma_deg_s: gamma,
      alpha_deg_s: alpha,
    };
    if ([row.ax, row.ay, row.az].every((v) => v !== null)) this.acceleration++;
    if ([row.gx, row.gy, row.gz].every((v) => v !== null)) this.gyroscope++;
    if (this.rows.length)
      this.maxGapUs = Math.max(this.maxGapUs, t_us - this.rows.at(-1)!.t_us);
    this.rows.push(row);
    return true;
  }
  summary() {
    const duration = (this.rows.at(-1)?.t_us ?? 0) / 1e6;
    return {
      count: this.rows.length,
      duration,
      hz: duration > 0 ? (this.rows.length - 1) / duration : null,
      maxGapMs: this.rows.length > 1 ? this.maxGapUs / 1000 : null,
      acceleration: this.acceleration,
      gyroscope: this.gyroscope,
    };
  }
  csv() {
    const keys: (keyof MotionRow)[] = [
      "t_us",
      "event_timestamp_ms",
      "ax",
      "ay",
      "az",
      "gx",
      "gy",
      "gz",
      "beta_deg_s",
      "gamma_deg_s",
      "alpha_deg_s",
    ];
    return (
      keys.join(",") +
      "\n" +
      this.rows.map((row) => keys.map((k) => row[k] ?? "").join(",")).join("\n")
    );
  }
}

export function downloadBlob(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
