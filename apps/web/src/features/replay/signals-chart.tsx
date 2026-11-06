"use client";
import { useMemo } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  usePlotArea,
  useXAxisInverseScale,
} from "recharts";
import { Sample } from "@/lib/api";
function SeekSurface({ onSeek }: { onSeek: (t: number) => void }) {
  const plot = usePlotArea(),
    invert = useXAxisInverseScale();
  if (!plot || !invert) return null;
  return (
    <rect
      x={plot.x}
      y={plot.y}
      width={plot.width}
      height={plot.height}
      fill="transparent"
      data-testid="plot-seek-surface"
      onClick={(event) => {
        const svg = event.currentTarget.ownerSVGElement,
          matrix = svg?.getScreenCTM();
        if (!svg || !matrix) return;
        const point = svg.createSVGPoint();
        point.x = event.clientX;
        point.y = event.clientY;
        const t = Number(invert(point.matrixTransform(matrix.inverse()).x));
        if (Number.isFinite(t)) onSeek(Math.round(t * 1e6));
      }}
    />
  );
}
export function SignalsChart({
  samples,
  timeUs,
  offsetUs,
  durationUs,
  kind,
  markers,
  onSeek,
  axes,
}: {
  samples: Sample[];
  timeUs: number;
  offsetUs: number;
  durationUs: number;
  kind: "gyro" | "acc";
  markers: number[];
  onSeek: (time: number) => void;
  axes: boolean;
}) {
  const data = useMemo(() => {
    const output: Array<Record<string, number | null>> = [];
    let previous: number | undefined;
    const intervals = samples
      .slice(1)
      .map((s, i) => s.t_us - samples[i].t_us)
      .sort((a, b) => a - b);
    const median = intervals[Math.floor(intervals.length / 2)] || 10_000;
    for (const s of samples) {
      if (previous !== undefined && s.t_us - previous > median * 3)
        output.push({
          t: (previous + s.t_us) / 2e6 + offsetUs / 1e6,
          acc: null,
          gyro: null,
          ax: null,
          ay: null,
          az: null,
          gx: null,
          gy: null,
          gz: null,
        });
      output.push({ ...s, t: (s.t_us + offsetUs) / 1e6 });
      previous = s.t_us;
    }
    return output;
  }, [samples, offsetUs]);
  const colors =
    kind === "gyro"
      ? ["#50d5b0", "#a7c8f0", "#dcad6c"]
      : ["#e5af70", "#a7c8f0", "#50d5b0"];
  return (
    <div className="signal-chart" data-testid={`${kind}-chart`}>
      <ResponsiveContainer width="100%" height={150}>
        <LineChart
          data={data}
          margin={{ top: 12, right: 20, bottom: 0, left: -20 }}
        >
          <CartesianGrid
            vertical={false}
            stroke="#25302e"
            strokeDasharray="3 5"
          />
          <XAxis
            dataKey="t"
            type="number"
            domain={[0, durationUs / 1e6]}
            allowDataOverflow
            tick={{ fill: "#738681", fontSize: 10 }}
            tickFormatter={(v) => `${v}s`}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#738681", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={55}
          />
          <Tooltip
            contentStyle={{
              background: "#17221f",
              border: "1px solid #34433e",
              borderRadius: 8,
              fontSize: 11,
            }}
            labelFormatter={(v) => `${Number(v).toFixed(3)} s`}
          />
          {markers.map((t, i) => (
            <ReferenceLine
              key={i}
              x={t / 1e6}
              stroke="#d5a466"
              strokeDasharray="3 5"
              strokeOpacity={0.4}
            />
          ))}
          <ReferenceLine x={timeUs / 1e6} stroke="#e5f0e9" strokeWidth={1.5} />
          {axes ? (
            (kind === "gyro" ? ["gx", "gy", "gz"] : ["ax", "ay", "az"]).map(
              (c, i) => (
                <Line
                  key={c}
                  type="linear"
                  dataKey={c}
                  stroke={colors[i]}
                  strokeWidth={1.2}
                  dot={false}
                  isAnimationActive={false}
                  connectNulls={false}
                />
              ),
            )
          ) : (
            <Line
              type="linear"
              dataKey={kind}
              stroke={colors[0]}
              strokeWidth={1.6}
              dot={false}
              isAnimationActive={false}
              connectNulls={false}
            />
          )}
          <SeekSurface onSeek={onSeek} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
