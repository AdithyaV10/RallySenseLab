import { memo, useEffect, useMemo, useState } from "react";
import type { MotionEvent, PoseFrame, SignalPoint } from "./data";
import { seconds } from "./data";

const bones = [
  [11, 12],
  [11, 23],
  [12, 24],
  [23, 24],
  [11, 13],
  [13, 15],
  [12, 14],
  [14, 16],
  [23, 25],
  [25, 27],
  [24, 26],
  [26, 28],
];
export function Pose({
  frame,
  hero = false,
}: {
  frame: PoseFrame;
  hero?: boolean;
}) {
  return (
    <svg
      viewBox="0 0 640 400"
      className={`pose ${hero ? "hero-pose" : ""}`}
      role="img"
      aria-label="Generated analytical pose observations, not MediaPipe inference"
    >
      <defs>
        <pattern
          id={hero ? "heroGrid" : "poseGrid"}
          width="40"
          height="40"
          patternUnits="userSpaceOnUse"
        >
          <path
            d="M40 0H0V40"
            fill="none"
            stroke="currentColor"
            strokeWidth=".6"
          />
        </pattern>
      </defs>
      <rect
        width="640"
        height="400"
        fill={`url(#${hero ? "heroGrid" : "poseGrid"})`}
        className="pose-grid"
      />
      <g className="court-lines" fill="none" strokeWidth="1">
        <path d="M88 355 203 112h235l114 243ZM88 355h464M146 233h348M320 112v243M201 112l-55 243M439 112l55 243" />
        <path d="M146 233h348" strokeDasharray="3 4" />
      </g>
      <ellipse
        cx="320"
        cy="355"
        rx="155"
        ry="18"
        fill="#73dfbb"
        opacity=".04"
      />
      <g transform="translate(82,-22) scale(.76,.88)" strokeLinecap="round">
        {bones
          .filter(
            ([a, b]) =>
              frame.landmarks[a].visibility > 0.5 &&
              frame.landmarks[b].visibility > 0.5,
          )
          .map(([a, b]) => (
            <line
              key={`${a}-${b}`}
              x1={frame.landmarks[a].x * 640}
              y1={frame.landmarks[a].y * 400}
              x2={frame.landmarks[b].x * 640}
              y2={frame.landmarks[b].y * 400}
              stroke={a === 14 || b === 14 || b === 16 ? "#8fe8c6" : "#96b7a5"}
              strokeWidth="3"
            />
          ))}
        {frame.landmarks.map((p, i) =>
          p.visibility > 0.5 ? (
            <circle
              key={i}
              cx={p.x * 640}
              cy={p.y * 400}
              r={i === 16 ? 6 : 3.5}
              fill={i === 16 ? "#e6bd87" : "#73dfbb"}
            />
          ) : null,
        )}
        <circle
          cx={frame.landmarks[16].x * 640}
          cy={frame.landmarks[16].y * 400}
          r="15"
          fill="none"
          stroke="#e6bd87"
          strokeOpacity=".35"
        />
      </g>
      <text x="22" y="30" className="svg-label">
        ANALYTICAL LANDMARKS
      </text>
      <text x="22" y="382" className="svg-label">
        KNOWN GENERATED CLOCK
      </text>
      <text x="525" y="382" className="svg-label">
        {seconds(frame.t_video_us)}
      </text>
    </svg>
  );
}

export function lineSegments(
  points: SignalPoint[],
  start: number,
  end: number,
  width: number,
  height: number,
) {
  const visible = points.filter(
    (p) => p.t_session_us >= start && p.t_session_us <= end,
  );
  const max =
    Math.max(0.001, ...points.map((p) => Math.abs(p.value ?? 0))) * 1.12;
  let segment = "",
    previous = -Infinity;
  const segments: string[] = [];
  for (const p of visible) {
    if (p.value == null || !Number.isFinite(p.value)) {
      if (segment) segments.push(segment);
      segment = "";
      previous = -Infinity;
      continue;
    }
    if (p.t_session_us - previous > 100000 && segment) {
      segments.push(segment);
      segment = "";
    }
    const x = 42 + ((p.t_session_us - start) / (end - start)) * (width - 60),
      y = height - 28 - (p.value / max) * (height - 48);
    segment += `${segment ? " L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`;
    previous = p.t_session_us;
  }
  if (segment) segments.push(segment);
  return { segments, max };
}

export const Signal = memo(function Signal({
  points,
  time,
  duration,
  label,
  unit,
  color = "var(--teal)",
  events = [],
  references = [],
  zoom = false,
  onSeek,
}: {
  points: SignalPoint[];
  time: number;
  duration: number;
  label: string;
  unit: string;
  color?: string;
  events?: MotionEvent[];
  references?: MotionEvent[];
  zoom?: boolean;
  onSeek?: (us: number) => void;
}) {
  const [compact, setCompact] = useState(
    () =>
      typeof window !== "undefined" &&
      window.matchMedia("(max-width:520px)").matches,
  );
  useEffect(() => {
    const q = window.matchMedia("(max-width:520px)");
    const update = () => setCompact(q.matches);
    q.addEventListener("change", update);
    return () => q.removeEventListener("change", update);
  }, []);
  const start = zoom
    ? Math.max(0, Math.min(time - 1000000, duration - 2000000))
    : 0;
  const end = zoom ? start + 2000000 : duration;
  const w = compact ? 520 : 900,
    h = compact ? 175 : 156;
  const { segments, max } = useMemo(
    () => lineSegments(points, start, end, w, h),
    [points, start, end, w, h],
  );
  const x = (us: number) => 42 + ((us - start) / (end - start)) * (w - 60);
  return (
    <section className="signal" aria-label={label}>
      <div className="signal-head">
        <span>
          <i style={{ background: color }} />
          {label}
        </span>
        <span>{unit}</span>
      </div>
      {points.length ? (
        <svg
          viewBox={`0 0 ${w} ${h}`}
          role="img"
          aria-label={`${label}. Select a point to seek the shared timeline.`}
          onClick={(event) => {
            const r = event.currentTarget.getBoundingClientRect();
            onSeek?.(
              Math.max(
                start,
                Math.min(
                  end,
                  start +
                    ((((event.clientX - r.left) / r.width) * w - 42) /
                      (w - 60)) *
                      (end - start),
                ),
              ),
            );
          }}
        >
          <title>
            {label} from stored observations; gaps remain disconnected.
          </title>
          {[0, 0.5, 1].map((v) => (
            <g key={v}>
              <line
                x1="42"
                x2="882"
                y1={h - 28 - v * (h - 48)}
                y2={h - 28 - v * (h - 48)}
                stroke="var(--line)"
                strokeDasharray="2 6"
              />
              <text x="4" y={h - 24 - v * (h - 48)} className="axis">
                {(max * v).toFixed(1)}
              </text>
            </g>
          ))}
          {references
            .filter((r) => r.t_session_us >= start && r.t_session_us <= end)
            .map((r, i) => (
              <line
                key={i}
                x1={x(r.t_session_us)}
                x2={x(r.t_session_us)}
                y1="14"
                y2={h - 28}
                stroke="var(--amber)"
                strokeOpacity=".4"
                strokeDasharray="3 5"
              />
            ))}
          {segments.map((d, i) => (
            <path key={i} d={d} fill="none" stroke={color} strokeWidth="2" />
          ))}
          {events
            .filter((e) => e.t_session_us >= start && e.t_session_us <= end)
            .map((e, i) => (
              <circle
                key={i}
                cx={x(e.t_session_us)}
                cy="12"
                r="3.5"
                fill={color}
              />
            ))}
          <line
            x1={x(time)}
            x2={x(time)}
            y1="5"
            y2={h - 28}
            stroke="#e7eee8"
            strokeWidth="1.3"
          />
          {[0, 1, 2, 3, 4].map((i) => (
            <text
              key={i}
              x={42 + (i * (w - 60)) / 4}
              y={h - 6}
              textAnchor={i === 0 ? "start" : i === 4 ? "end" : "middle"}
              className="axis"
            >
              {seconds(start + (i * (end - start)) / 4, 1)}
            </text>
          ))}
        </svg>
      ) : (
        <div className="unavailable">
          This stored run has no observations for this modality.
        </div>
      )}
    </section>
  );
});
