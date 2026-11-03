import type { components } from "./schema";
export type LabSession = components["schemas"]["SessionOut"];
export type SessionDetail = components["schemas"]["SessionDetail"];
export type Sensor = components["schemas"]["SensorOut"];
export type Video = components["schemas"]["VideoOut"];
export type Pose = components["schemas"]["PoseOut"];
export type PoseFrame = components["schemas"]["PoseFrame"];
export type Sample = components["schemas"]["Sample"];
export type Samples = components["schemas"]["SamplesOut"];
export type Annotation = components["schemas"]["AnnotationOut"];
export type DetectorConfig = components["schemas"]["DetectorConfig"];
export type SensorMapping = components["schemas"]["SensorMapping"];

export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("x-lab-client", "rallysense");
  if (options.body && !(options.body instanceof FormData))
    headers.set("content-type", "application/json");
  const response = await fetch(`/api/v1${path}`, { ...options, headers });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const error = await response.json();
      message = error.error?.message || message;
    } catch {
      /* retain status */
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const numeric = (value: unknown, fallback = 0): number =>
  typeof value === "number" ? value : fallback;
export const seconds = (us: number) => us / 1_000_000;
export const provenanceLabel = (kind: string) =>
  kind === "synthetic"
    ? "Synthetic fixture"
    : kind === "mixed"
      ? "Mixed sources"
      : "Recorded observations";
export function clock(us: number) {
  const s = Math.max(0, us / 1e6);
  return `${Math.floor(s / 60)
    .toString()
    .padStart(2, "0")}:${(s % 60).toFixed(2).padStart(5, "0")}`;
}
