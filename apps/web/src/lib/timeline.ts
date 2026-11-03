export const toSession = (sourceUs: number, offsetUs: number) =>
  sourceUs + offsetUs;
export const toSource = (sessionUs: number, offsetUs: number) =>
  sessionUs - offsetUs;
export const roundHalfAway = (value: number) =>
  Math.sign(value) * Math.floor(Math.abs(value) + 0.5);
export function containRect(
  width: number,
  height: number,
  containerWidth: number,
  containerHeight: number,
) {
  const scale = Math.min(containerWidth / width, containerHeight / height);
  return { width: width * scale, height: height * scale };
}
export function nearestFrame<T extends { t_video_us: number }>(
  frames: T[],
  t: number,
  maxAge = 100_000,
): T | null {
  let lo = 0,
    hi = frames.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (frames[mid].t_video_us < t) lo = mid + 1;
    else hi = mid;
  }
  const candidates = [frames[lo - 1], frames[lo]].filter(Boolean);
  const closest = candidates.sort(
    (a, b) => Math.abs(a.t_video_us - t) - Math.abs(b.t_video_us - t),
  )[0];
  return closest && Math.abs(closest.t_video_us - t) <= maxAge ? closest : null;
}
