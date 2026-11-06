import type { components } from "@/lib/schema";
export type Experiment = components["schemas"]["ExperimentOut"];
export type ExperimentRequest = components["schemas"]["ExperimentCreate"];
export type Reference = components["schemas"]["ReferenceOut"];
export type LabelSet = components["schemas"]["AnnotationSetOut"];
export type FreezeRequest = components["schemas"]["FreezeCreate"];
export type ResearchEvent = components["schemas"]["ResearchEvent"];
export const record = (value: unknown): Record<string, unknown> =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
export function modeOf(run: Experiment) {
  return String(record(run.manifest.request).mode || "unknown");
}
export const percent = (v: number | null | undefined) =>
  v == null ? "—" : `${(v * 100).toFixed(1)}%`;
export const millis = (v: number | null | undefined) =>
  v == null ? "—" : `${(v / 1000).toFixed(1)} ms`;

export function modeUnavailable(
  mode: string,
  sensor: boolean,
  pose: boolean,
  kind: string,
) {
  if (mode === "video" && !pose)
    return "Extract a pose track from video first.";
  if (mode === "imu" && !sensor) return "Import a gyroscope recording first.";
  if (mode === "fusion" && (!sensor || !pose))
    return "Both a sensor recording and a ready pose track are required.";
  if (mode === "fusion" && kind === "mixed")
    return "Mixed sources are not physically paired; fusion is unavailable.";
  return "";
}
