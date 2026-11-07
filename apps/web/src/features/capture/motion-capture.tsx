"use client";
import { useEffect, useRef, useState } from "react";
import { Activity, Download, Radio, Square } from "lucide-react";
import type { components } from "@/lib/schema";
import { api, type SessionDetail } from "@/lib/api";
import { Badge, ErrorBox } from "@/components/ui";
import { MotionBuffer, downloadBlob, type AccelerationKind } from "./motion";

type PermissionConstructor = typeof DeviceMotionEvent & {
  requestPermission?: () => Promise<string>;
};
type CaptureMetadata = components["schemas"]["CaptureMetadata"];
export function MotionCapture({
  session,
  refresh,
}: {
  session: SessionDetail;
  refresh: () => void;
}) {
  const buffer = useRef(new MotionBuffer("linear"));
  const [kind, setKind] = useState<AccelerationKind>("linear");
  const [provenance, setProvenance] = useState<"recorded" | "synthetic">(
    "recorded",
  );
  const [recording, setRecording] = useState(false);
  const [view, setView] = useState({
    summary: new MotionBuffer("linear").summary(),
    points: "",
    cueCount: 0,
  });
  const [status, setStatus] = useState("Ready to request motion access"),
    [error, setError] = useState<unknown>(null),
    [busy, setBusy] = useState(false);
  const metadata = useRef<CaptureMetadata | null>(null);
  const saved = useRef(true),
    cues = useRef<number[]>([]);
  const stopRef = useRef<(reason: string) => void>(() => {});
  useEffect(() => {
    if (!recording) return;
    let lastArrival = performance.now();
    const listener = (event: DeviceMotionEvent) => {
      lastArrival = performance.now();
      if (
        buffer.current.firstTimestamp !== null &&
        event.timeStamp - buffer.current.firstTimestamp > 1_200_000
      ) {
        stopRef.current("20 minute recording limit reached");
        return;
      }
      if (
        !buffer.current.append(event) &&
        (buffer.current.rows.length >= 120000 ||
          (buffer.current.rows.at(-1)?.t_us ?? 0) >= 1_199_000_000)
      )
        stopRef.current("Recording limit reached");
      saved.current = false;
    };
    const visibility = () => {
      if (document.hidden)
        stopRef.current("Page hidden / screen locked; recording interrupted");
    };
    const pagehide = () =>
      stopRef.current("Page navigation interrupted recording");
    const orientation = () =>
      stopRef.current(
        "Device orientation changed; begin a new recording to keep axes interpretable",
      );
    window.addEventListener("devicemotion", listener);
    document.addEventListener("visibilitychange", visibility);
    window.addEventListener("pagehide", pagehide);
    screen.orientation?.addEventListener("change", orientation);
    const interval = setInterval(() => {
      updateView();
      if (performance.now() - lastArrival > 10_000)
        stopRef.current(
          "No motion events for 10 seconds. Use CSV export from a supported sensor app.",
        );
    }, 200);
    return () => {
      clearInterval(interval);
      window.removeEventListener("devicemotion", listener);
      document.removeEventListener("visibilitychange", visibility);
      window.removeEventListener("pagehide", pagehide);
      screen.orientation?.removeEventListener("change", orientation);
    };
  }, [recording]);
  useEffect(() => {
    const guard = (event: BeforeUnloadEvent) => {
      if (!saved.current && buffer.current.rows.length) event.preventDefault();
    };
    window.addEventListener("beforeunload", guard);
    return () => window.removeEventListener("beforeunload", guard);
  }, []);
  function stop(reason: string) {
    setRecording(false);
    setStatus(reason);
    if (metadata.current) metadata.current.stop_reason = reason;
    updateView();
  }
  useEffect(() => {
    stopRef.current = stop;
  });
  async function start() {
    setError(null);
    try {
      if (!window.isSecureContext)
        throw new Error(
          "Motion capture requires HTTPS or localhost. Import CSV here, or use the documented trusted local HTTPS workflow.",
        );
      if (typeof DeviceMotionEvent === "undefined")
        throw new Error(
          "This browser has no DeviceMotion API. Export CSV from phyphox or another sensor app, then import below.",
        );
      if (
        !saved.current &&
        buffer.current.rows.length &&
        !window.confirm(
          "Replace unsaved motion capture? Export or save it first to retain it.",
        )
      )
        return;
      // Permission is invoked directly in this user gesture, before any other asynchronous work.
      const permission = (DeviceMotionEvent as PermissionConstructor)
        .requestPermission;
      if (
        permission &&
        (await permission.call(DeviceMotionEvent)) !== "granted"
      )
        throw new Error(
          "Motion permission denied. Enable motion access in browser settings, or use CSV import.",
        );
      buffer.current = new MotionBuffer(kind);
      cues.current = [];
      saved.current = true;
      metadata.current = {
        source: "browser_devicemotion",
        stop_reason: "operator",
        discarded_timestamps: 0,
        sample_count: 0,
        device_model: String(
          session.collection_profile.device_model ?? "unknown",
        ),
        started_at_utc: new Date().toISOString(),
        timestamp_basis:
          "DeviceMotionEvent.timeStamp; first accepted event normalized to zero; not a shared camera clock",
        time_origin_ms: performance.timeOrigin,
        coordinate_frame:
          "raw device frame; no world-frame transformation or attitude estimate",
        axis_mapping:
          "beta -> gx, gamma -> gy, alpha -> gz; degrees/s converted to radians/s",
        acceleration_kind: kind,
        source_rotation_unit: "deg/s",
        orientation_angle_deg: screen.orientation?.angle ?? null,
        browser: navigator.userAgent.slice(0, 400),
      };
      setRecording(true);
      setStatus(
        "Waiting for actual motion events. Keep this page visible and the screen unlocked.",
      );
    } catch (e) {
      setError(e);
    }
  }
  function captureMetadata(): CaptureMetadata {
    return {
      ...metadata.current!,
      original_first_timestamp_ms: buffer.current.firstTimestamp,
      discarded_timestamps: buffer.current.discarded,
      sample_count: buffer.current.rows.length,
      operator_cues_us: cues.current,
    };
  }
  async function save() {
    setBusy(true);
    setError(null);
    try {
      const s = buffer.current.summary();
      if (s.count < 2 || (!s.acceleration && !s.gyroscope))
        throw new Error(
          "No complete xyz stream was received. Export the raw CSV for inspection or use a native sensor app.",
        );
      const form = new FormData();
      form.set(
        "file",
        new File([buffer.current.csv()], "browser-motion.csv", {
          type: "text/csv",
        }),
      );
      form.set(
        "mapping",
        JSON.stringify({
          timestamp: "t_us",
          time_unit: "us",
          acceleration: s.acceleration ? ["ax", "ay", "az"] : [],
          gyroscope: s.gyroscope ? ["gx", "gy", "gz"] : [],
          acceleration_unit: "m/s2",
          gyroscope_unit: "rad/s",
          acceleration_kind: kind,
          placement: String(
            session.collection_profile.sensor_placement ?? "unknown",
          ).slice(0, 80),
          provenance,
          capture: captureMetadata(),
        }),
      );
      await api(`/sessions/${session.id}/sensor-imports`, {
        method: "POST",
        body: form,
      });
      saved.current = true;
      setStatus(
        "Saved for validation. Inspect the processing job and quality report below.",
      );
      refresh();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  function updateView() {
    const points = buffer.current.rows
      .slice(-100)
      .map((r, i) => {
        const g =
          r.gx === null || r.gy === null || r.gz === null
            ? null
            : Math.hypot(r.gx, r.gy, r.gz);
        return g === null ? null : `${i * 3},${76 - Math.min(70, g * 8)}`;
      })
      .filter(Boolean)
      .join(" ");
    setView({
      summary: buffer.current.summary(),
      points,
      cueCount: cues.current.length,
    });
  }
  const { summary, points, cueCount } = view;
  return (
    <section className="panel capture-card">
      <div className="capture-card-title">
        <Activity size={20} />
        <h2>Phone motion</h2>
        <Badge tone={recording ? "teal" : "neutral"}>
          {recording ? "LIVE OBSERVATIONS" : "DEVICE MOTION"}
        </Badge>
      </div>
      <p>
        Actual acceleration and angular rate in raw device axes. No orientation,
        swing classification or calibration is inferred.
      </p>
      <label>
        Motion source provenance
        <select
          aria-label="Motion source provenance"
          value={provenance}
          disabled={recording || summary.count > 0}
          onChange={(e) => setProvenance(e.target.value as typeof provenance)}
        >
          <option value="recorded">Recorded device observations</option>
          <option value="synthetic">Synthetic injected software test</option>
        </select>
      </label>
      <label>
        Acceleration quantity
        <select
          value={kind}
          disabled={recording || summary.count > 0}
          onChange={(e) => setKind(e.target.value as AccelerationKind)}
        >
          <option value="linear">
            Linear acceleration (gravity excluded by device)
          </option>
          <option value="including_gravity">
            Acceleration including gravity
          </option>
        </select>
      </label>
      <svg
        viewBox="0 0 300 84"
        className="live-motion"
        role="img"
        aria-label="Live measured angular-speed magnitude, radians per second"
      >
        <path d="M0 76H300" stroke="var(--border)" />
        <polyline
          fill="none"
          stroke="var(--teal, #4edac0)"
          strokeWidth="2"
          points={points}
        />
      </svg>
      <div className="capture-stats">
        <span>
          <b>{summary.count.toLocaleString()}</b> samples
        </span>
        <span>
          <b>{summary.duration.toFixed(1)} s</b> observed
        </span>
        <span>
          <b>{summary.hz?.toFixed(1) ?? "—"} Hz</b> mean cadence
        </span>
      </div>
      <p className="capture-status" role="status">
        {recording && summary.count > 0
          ? "Receiving measurements. Keep this page visible."
          : status}
      </p>
      {summary.count > 0 && (
        <p>
          Complete acceleration: {summary.acceleration}/{summary.count};
          rotation rate: {summary.gyroscope}/{summary.count}. Largest observed
          gap: {summary.maxGapMs?.toFixed(1) ?? "—"} ms. Missing values remain
          missing.
        </p>
      )}
      <div className="capture-actions">
        {!recording && summary.count > 0 && (
          <button
            className="button ghost"
            onClick={() => {
              if (
                !saved.current &&
                !window.confirm(
                  "Clear unsaved observations? Save or export first to retain them.",
                )
              )
                return;
              buffer.current = new MotionBuffer(kind);
              cues.current = [];
              metadata.current = null;
              saved.current = true;
              setStatus("Ready for a new capture");
              updateView();
            }}
          >
            Clear capture / change quantity
          </button>
        )}
        {recording ? (
          <>
            <button
              className="button danger"
              onClick={() => stop("Stopped by operator")}
            >
              <Square size={14} />
              Stop motion
            </button>
            <button
              className="button"
              disabled={cueCount >= 2 || !summary.count}
              onClick={() => {
                cues.current.push(buffer.current.rows.at(-1)!.t_us);
                updateView();
              }}
            >
              Mark operator cue ({cueCount}/2)
            </button>
          </>
        ) : (
          <button className="button primary" onClick={start}>
            <Radio size={15} />
            Start motion capture
          </button>
        )}
        <button
          className="button"
          disabled={recording || !summary.count}
          onClick={() => {
            downloadBlob(
              new Blob([buffer.current.csv()], { type: "text/csv" }),
              "motion.csv",
            );
            downloadBlob(
              new Blob([JSON.stringify(captureMetadata(), null, 2)], {
                type: "application/json",
              }),
              "motion-metadata.json",
            );
          }}
        >
          <Download size={15} />
          Export raw CSV + metadata
        </button>
        <button
          className="button"
          disabled={recording || busy || !summary.count}
          onClick={save}
        >
          {busy ? "Saving…" : "Save motion to session"}
        </button>
      </div>
      <ErrorBox error={error} />
      <p className="fine-print">
        Capture is held in memory until saved or exported; reloading can lose
        it. Operator cues are rough manual markers, not ground truth.
        Unsupported or denied device access: use phyphox CSV import below.
        Physical iOS/Android behavior has not been verified here.
      </p>
    </section>
  );
}
