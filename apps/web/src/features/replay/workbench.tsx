"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  ArrowLeft,
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  Clock3,
  FileVideo,
  Layers3,
  Pause,
  Play,
  Plus,
  ScanLine,
  Settings2,
  SkipBack,
  SkipForward,
  SlidersHorizontal,
  Upload,
} from "lucide-react";
import {
  api,
  SessionDetail,
  Samples,
  PoseFrame,
  numeric,
  clock,
  DetectorConfig,
  provenanceLabel,
} from "@/lib/api";
import { Badge, ErrorBox, Loading, Shell } from "@/components/ui";
import { DataManager } from "@/features/ingestion/data-manager";
import { ReplayMedia } from "./replay-media";
import { SignalsChart } from "./signals-chart";
import { EventPanel } from "./event-panel";
import { extractPose } from "./pose-extraction";
import { Challenge } from "@/features/research/challenge";

const defaultConfig: DetectorConfig = {
  cutoff_hz: 8,
  threshold_rad_s: 1,
  prominence_rad_s: 0.5,
  min_separation_s: 0.3,
  adaptive_k: 3,
};
export function Workbench({
  id,
  initialTab = "replay",
}: {
  id: string;
  initialTab?: string;
}) {
  const query = useQueryClient();
  const [tab, setTab] = useState(initialTab),
    [timeUs, setTimeUs] = useState(0),
    [playing, setPlaying] = useState(false),
    [rate, setRate] = useState(1),
    [seekToken, setSeekToken] = useState(0),
    [axes, setAxes] = useState(false),
    [blind, setBlind] = useState(false);
  const [selectedSensor, setSelectedSensor] = useState(""),
    [selectedVideo, setSelectedVideo] = useState("");
  const [error, setError] = useState<unknown>(null),
    [busy, setBusy] = useState(""),
    [poseMessage, setPoseMessage] = useState(""),
    [offsetDraft, setOffsetDraft] = useState<string | null>(null),
    [config, setConfig] = useState<DetectorConfig>(defaultConfig),
    [showConfig, setShowConfig] = useState(false);
  const abort = useRef<AbortController | null>(null);
  const [poseTarget, setPoseTarget] = useState<10 | 30>(10);
  const cursor = useRef(0);
  useEffect(() => {
    cursor.current = timeUs;
  }, [timeUs]);
  const session = useQuery({
    queryKey: ["session", id],
    queryFn: () => api<SessionDetail>(`/sessions/${id}`),
    refetchInterval: (q) =>
      q.state.data?.jobs.some((j) => ["queued", "running"].includes(j.state))
        ? 1000
        : 5000,
  });
  const data = session.data,
    sensors = data?.sensors.filter((s) => s.status === "ready") || [],
    videos = data?.videos.filter((v) => v.status === "ready") || [];
  const sensor = sensors.find((s) => s.id === selectedSensor) || sensors[0],
    video = videos.find((v) => v.id === selectedVideo) || videos[0];
  const sync = data?.syncs.filter((s) => s.sensor_id === sensor?.id).at(-1),
    offsetUs = sync?.offset_us || 0;
  const run = data?.runs.filter((r) => r.sensor_id === sensor?.id).at(-1);
  const predictions =
    data?.predictions.filter((p) => p.run_id === run?.id) || [];
  const pose = data?.poses
    .filter((p) => p.video_id === video?.id && p.status === "ready")
    .at(-1);
  const samples = useQuery({
    queryKey: ["samples", sensor?.id],
    queryFn: () => api<Samples>(`/sensor-recordings/${sensor!.id}/samples`),
    enabled: !!sensor,
    staleTime: Infinity,
  });
  const frames = useQuery({
    queryKey: ["pose", pose?.id],
    queryFn: () =>
      api<{ frames: PoseFrame[] }>(`/pose-tracks/${pose!.id}/frames`),
    enabled: !!pose,
    staleTime: Infinity,
  });
  const durationUs = Number(
    video?.duration_us ||
      Math.max(0, (sensor?.duration_us || 0) + offsetUs) ||
      18e6,
  );
  const refresh = useCallback(() => {
    query.invalidateQueries({ queryKey: ["session", id] });
  }, [query, id]);
  const seek = useCallback(
    (t: number) => {
      setTimeUs(Math.max(0, Math.min(t, durationUs)));
      setSeekToken((v) => v + 1);
    },
    [durationUs],
  );
  useEffect(() => {
    if (!playing || video) return;
    let last = performance.now(),
      frame = 0;
    const tick = (now: number) => {
      const elapsed = (now - last) * 1000;
      if (elapsed >= 60_000) {
        const delta = elapsed * rate;
        last = now;
        const next = Math.min(cursor.current + delta, durationUs);
        cursor.current = next;
        setTimeUs(next);
        if (next >= durationUs) setPlaying(false);
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, rate, video, durationUs]);
  useEffect(() => () => abort.current?.abort(), []);
  useEffect(() => {
    function key(e: KeyboardEvent) {
      if ((e.target as HTMLElement).matches("input,textarea,select,button"))
        return;
      if (e.code === "Space") {
        e.preventDefault();
        setPlaying((p) => !p);
      }
      if (e.code === "ArrowRight") {
        e.preventDefault();
        seek(timeUs + 100_000);
      }
      if (e.code === "ArrowLeft") {
        e.preventDefault();
        seek(timeUs - 100_000);
      }
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [seek, timeUs]);
  async function action(label: string, fn: () => Promise<unknown>) {
    setBusy(label);
    setError(null);
    try {
      await fn();
      refresh();
    } catch (e) {
      setError(e);
    } finally {
      setBusy("");
    }
  }
  async function analyze() {
    if (!sensor) return;
    await action("analyze", () =>
      api(`/sessions/${id}/inference-runs`, {
        method: "POST",
        body: JSON.stringify({ sensor_id: sensor.id, config }),
      }),
    );
  }
  function togglePlay() {
    if (timeUs >= durationUs) seek(0);
    setPlaying((p) => !p);
  }
  if (session.isLoading)
    return (
      <Shell>
        <Loading label="Loading session observations" />
      </Shell>
    );
  if (!data)
    return (
      <Shell>
        <div className="page-content">
          <ErrorBox error={session.error || "Session unavailable"} />
          <Link href="/sessions" className="button secondary">
            Return to sessions
          </Link>
        </div>
      </Shell>
    );
  return (
    <Shell>
      <div className="workbench">
        <div className="breadcrumb">
          <Link href="/sessions">
            <ArrowLeft size={13} />
            Session library
          </Link>
          <span>/</span>
          <span>{id.slice(0, 8)}</span>
          <Badge tone={data.dataset_kind === "synthetic" ? "amber" : "neutral"}>
            {provenanceLabel(data.dataset_kind)}
          </Badge>
        </div>
        <div className="workbench-heading">
          <div>
            <div className="eyebrow">MOVEMENT OBSERVATORY</div>
            <h1>{data.title}</h1>
            <p>
              {data.dataset_kind === "synthetic"
                ? "Synthetic software demonstration. No real-world athlete validation."
                : "Synchronized observations. Inspect the signal and its limitations."}
            </p>
          </div>
          <button className="button secondary" onClick={() => setTab("data")}>
            <Upload size={15} />
            Add recording
          </button>
        </div>
        <div className="workspace-tabs">
          <button
            className={tab === "replay" ? "active" : ""}
            onClick={() => setTab("replay")}
          >
            <Play size={14} />
            Synchronized replay
          </button>
          <button
            className={tab === "data" ? "active" : ""}
            onClick={() => setTab("data")}
          >
            <Layers3 size={15} />
            Data & processing
            <span>{data.sensors.length + data.videos.length}</span>
          </button>
          <div className="workspace-status">
            <i />
            {data.jobs.some((j) => ["queued", "running"].includes(j.state))
              ? "Processing observations"
              : "Workspace synchronized"}
          </div>
          <button
            className={tab === "research" ? "active" : ""}
            onClick={() => {
              setPlaying(false);
              setTab("research");
            }}
          >
            <Activity size={15} /> Sensor Fusion Challenge
          </button>
        </div>
        <ErrorBox error={error || samples.error || frames.error} />
        {data.jobs
          .filter((j) => j.state === "failed")
          .slice(-1)
          .map((j) => (
            <ErrorBox key={j.id} error={`${j.kind}: ${j.error}`} />
          ))}
        {tab === "research" ? (
          <Challenge
            session={data}
            refreshSession={refresh}
            onSeek={(t) => {
              setTab("replay");
              setPlaying(false);
              seek(t);
            }}
          />
        ) : tab === "data" ? (
          <DataManager session={data} refresh={refresh} />
        ) : (
          <>
            <div className="measurement-strip">
              <div>
                <span className="metric-icon">
                  <Clock3 size={17} />
                </span>
                <span>
                  <small>OBSERVATION WINDOW</small>
                  <strong>
                    {(durationUs / 1e6).toFixed(2)} <em>s</em>
                  </strong>
                </span>
              </div>
              <div>
                <span className="metric-icon">
                  <Activity size={17} />
                </span>
                <span>
                  <small>SENSOR CADENCE</small>
                  <strong>
                    {sensor
                      ? numeric(sensor.quality.sample_rate_hz).toFixed(1)
                      : "—"}{" "}
                    <em>Hz</em>
                  </strong>
                </span>
              </div>
              <div>
                <span className="metric-icon amber">
                  <Activity size={17} />
                </span>
                <span>
                  <small>COMPUTED GYRO PEAKS</small>
                  <strong>
                    {blind
                      ? "Hidden"
                      : run?.status === "succeeded"
                        ? predictions.length
                        : "—"}
                    <em> signal events</em>
                  </strong>
                </span>
              </div>
              <div>
                <span className="metric-icon">
                  <ScanLine size={17} />
                </span>
                <span>
                  <small>POSE OBSERVATIONS</small>
                  <strong>
                    {pose ? numeric(pose.quality.detected_frames) : "—"}
                    <em>{pose ? " frames" : "not extracted"}</em>
                  </strong>
                </span>
              </div>
            </div>
            {(sensors.length > 1 || videos.length > 1) && (
              <div className="source-selectors">
                {sensors.length > 1 && (
                  <label>
                    Sensor{" "}
                    <select
                      value={sensor?.id}
                      onChange={(e) => {
                        setSelectedSensor(e.target.value);
                        setOffsetDraft(null);
                      }}
                    >
                      {sensors.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </label>
                )}
                {videos.length > 1 && (
                  <label>
                    Video{" "}
                    <select
                      value={video?.id}
                      onChange={(e) => {
                        setSelectedVideo(e.target.value);
                        seek(0);
                      }}
                    >
                      {videos.map((v) => (
                        <option key={v.id} value={v.id}>
                          {v.name}
                        </option>
                      ))}
                    </select>
                  </label>
                )}
              </div>
            )}
            <div className="replay-grid">
              <div className="replay-left">
                <ReplayMedia
                  video={video}
                  frames={frames.data?.frames || []}
                  timeUs={timeUs}
                  playing={playing}
                  rate={rate}
                  onTime={setTimeUs}
                  onEnded={() => setPlaying(false)}
                  synthetic={data.dataset_kind === "synthetic"}
                  seekToken={seekToken}
                  generatedLandmarks={
                    pose?.config.provenance === "generated_analytical_landmarks"
                  }
                />
                <div className="transport">
                  <button
                    className="icon-button"
                    aria-label="Jump to start"
                    onClick={() => seek(0)}
                  >
                    <SkipBack size={16} />
                  </button>
                  <button
                    className="icon-button"
                    aria-label="Previous signal event"
                    disabled={blind}
                    onClick={() =>
                      seek(
                        predictions
                          .filter((p) => p.t_session_us < timeUs - 1000)
                          .at(-1)?.t_session_us || 0,
                      )
                    }
                  >
                    <ChevronLeft size={17} />
                  </button>
                  <button
                    className="play-button"
                    aria-label={playing ? "Pause playback" : "Play playback"}
                    onClick={togglePlay}
                  >
                    {playing ? (
                      <Pause size={18} />
                    ) : (
                      <Play size={18} fill="currentColor" />
                    )}
                  </button>
                  <button
                    className="icon-button"
                    aria-label="Next signal event"
                    disabled={blind}
                    onClick={() =>
                      seek(
                        predictions.find((p) => p.t_session_us > timeUs + 1000)
                          ?.t_session_us || durationUs,
                      )
                    }
                  >
                    <ChevronRight size={17} />
                  </button>
                  <button
                    className="icon-button"
                    aria-label="Jump to end"
                    onClick={() => seek(durationUs)}
                  >
                    <SkipForward size={16} />
                  </button>
                  <span className="transport-time" data-testid="playback-time">
                    {clock(timeUs)}
                    <i>/ {clock(durationUs)}</i>
                  </span>
                  <label className="speed-select">
                    <select
                      aria-label="Playback speed"
                      value={rate}
                      onChange={(e) => setRate(Number(e.target.value))}
                    >
                      {[0.25, 0.5, 1, 1.5, 2].map((r) => (
                        <option key={r} value={r}>
                          {r}×
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <div className="timeline">
                  <input
                    type="range"
                    aria-label="Session timeline"
                    min="0"
                    max={durationUs}
                    step="1000"
                    value={timeUs}
                    onChange={(e) => seek(Number(e.target.value))}
                  />
                  <div className="timeline-event-lane">
                    {!blind &&
                      predictions.map((p) => (
                        <button
                          key={p.id}
                          title={`Gyro peak ${clock(p.t_session_us)}`}
                          aria-label={`Seek gyro peak ${clock(p.t_session_us)}`}
                          style={{
                            left: `${(p.t_session_us / durationUs) * 100}%`,
                          }}
                          className="timeline-marker prediction"
                          onClick={() => seek(p.t_session_us)}
                        />
                      ))}
                    {data.annotations.map((a) => (
                      <button
                        key={a.id}
                        title={`${a.event_type} ${clock(a.t_session_us)}`}
                        aria-label={`Seek reference ${clock(a.t_session_us)}`}
                        style={{
                          left: `${(a.t_session_us / durationUs) * 100}%`,
                        }}
                        className="timeline-marker reference"
                        onClick={() => seek(a.t_session_us)}
                      />
                    ))}
                  </div>
                  <div className="timeline-labels">
                    <span>00:00</span>
                    <div>
                      <i className="legend-dot amber" />
                      Signal event <i className="legend-dot teal" />
                      Reference
                    </div>
                    <span>{clock(durationUs)}</span>
                  </div>
                </div>
                {video && (
                  <div className="pose-action">
                    <div>
                      <ScanLine size={16} />
                      <span>
                        {pose
                          ? `${pose.config.provenance === "generated_analytical_landmarks" ? "Generated fixture landmarks (not MediaPipe)" : "MediaPipe"} · ${numeric(pose.quality.processed_frames)} sampled frames · ${(numeric(pose.quality.detection_fraction) * 100).toFixed(0)}% with detection`
                          : "Extract timestamped pose landmarks from this video."}
                      </span>
                    </div>
                    <select
                      aria-label="Pose sampling target"
                      value={poseTarget}
                      disabled={!!busy}
                      onChange={(e) =>
                        setPoseTarget(Number(e.target.value) as 10 | 30)
                      }
                    >
                      <option value={10}>10 Hz / standard</option>
                      <option value={30}>30 Hz / slow extraction</option>
                    </select>
                    {busy === "pose" ? (
                      <button
                        className="button secondary small"
                        onClick={() => abort.current?.abort()}
                      >
                        Cancel extraction
                      </button>
                    ) : (
                      <button
                        className="button secondary small"
                        disabled={!!busy}
                        onClick={() =>
                          action("pose", async () => {
                            setPlaying(false);
                            abort.current = new AbortController();
                            await extractPose(
                              video.id,
                              setPoseMessage,
                              abort.current.signal,
                              poseTarget,
                            );
                          })
                        }
                      >
                        <ScanLine size={13} />
                        {pose ? "Extract new track" : "Extract pose"}
                      </button>
                    )}
                  </div>
                )}
                {poseMessage && (
                  <p className="processing-message" role="status">
                    {poseMessage}
                  </p>
                )}
              </div>
              <EventPanel
                session={data}
                timeUs={timeUs}
                onSeek={seek}
                refresh={refresh}
                runId={blind ? undefined : run?.id}
                blind={blind}
                onError={setError}
              />
            </div>
            <div className="signal-section-heading">
              <div>
                <div className="eyebrow">THE SIGNAL BENEATH THE MOVEMENT</div>
                <h2>Inertial observations</h2>
              </div>
              <div className="signal-toggles">
                <label>
                  <input
                    type="checkbox"
                    checked={axes}
                    onChange={(e) => setAxes(e.target.checked)}
                  />
                  Show xyz
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={blind}
                    onChange={(e) => setBlind(e.target.checked)}
                  />
                  Blinded labels
                </label>
              </div>
            </div>
            {!blind && (
              <div className="signal-stack">
                {sensor && samples.data ? (
                  [
                    {
                      kind: "gyro" as const,
                      title: "Angular velocity",
                      unit: "rad/s",
                      color: "teal",
                    },
                    {
                      kind: "acc" as const,
                      title: "Acceleration",
                      unit: "m/s²",
                      color: "amber",
                    },
                  ].map((p) => (
                    <div className="panel signal-panel" key={p.kind}>
                      <div className="panel-heading">
                        <div className="panel-title">
                          <i className={`legend-dot ${p.color}`} />
                          <h3>{p.title}</h3>
                          <span className="signal-unit">{p.unit}</span>
                        </div>
                        <span className="muted">
                          {axes ? "x / y / z" : "vector magnitude"} · source
                          observations
                        </span>
                      </div>
                      <SignalsChart
                        samples={samples.data.data}
                        timeUs={timeUs}
                        offsetUs={offsetUs}
                        durationUs={durationUs}
                        kind={p.kind}
                        axes={axes}
                        markers={predictions.map((e) => e.t_session_us)}
                        onSeek={seek}
                      />
                    </div>
                  ))
                ) : (
                  <div className="panel empty-state">
                    <Activity size={26} />
                    <h3>Add a sensor recording</h3>
                    <p>
                      Upload a CSV to inspect normalized signals and compute
                      events.
                    </p>
                    <button
                      className="button secondary"
                      onClick={() => setTab("data")}
                    >
                      <Plus size={14} />
                      Import measurements
                    </button>
                  </div>
                )}
              </div>
            )}
            <div className="analysis-grid">
              <section className="panel alignment-panel">
                <div className="panel-heading">
                  <h3>
                    <SlidersHorizontal size={16} />
                    Clock alignment
                  </h3>
                  <Badge>Revision {sync?.revision || "—"}</Badge>
                </div>
                <p>
                  Positive offsets move sensor events later on the video
                  timeline.
                </p>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (sensor)
                      action("sync", async () => {
                        await api(`/sessions/${id}/sync-configurations`, {
                          method: "POST",
                          body: JSON.stringify({
                            sensor_id: sensor.id,
                            offset_us: Math.round(
                              Number(offsetDraft ?? offsetUs / 1e6) * 1e6,
                            ),
                          }),
                        });
                        setOffsetDraft(null);
                      });
                  }}
                >
                  <label className="offset-field">
                    <span>IMU OFFSET</span>
                    <input
                      aria-label="Sensor offset in seconds"
                      type="number"
                      step=".01"
                      min="-600"
                      max="600"
                      value={offsetDraft ?? offsetUs / 1e6}
                      onChange={(e) => setOffsetDraft(e.target.value)}
                    />
                    <span>s</span>
                  </label>
                  <button
                    className="button secondary"
                    disabled={!sensor || !!busy}
                  >
                    Save alignment
                  </button>
                </form>
                {run && run.sync_id !== sync?.id && (
                  <p className="amber-text">
                    The displayed run uses an earlier alignment. Run the
                    baseline again to apply this revision.
                  </p>
                )}
                <small>Existing results retain their original alignment.</small>
              </section>
              <section className="panel baseline-panel">
                <div className="panel-heading">
                  <h3>
                    <Activity size={16} />
                    IMU analytical baseline
                  </h3>
                  <button
                    className="icon-button"
                    aria-label="Configure detector"
                    onClick={() => setShowConfig(!showConfig)}
                  >
                    <Settings2 size={16} />
                  </button>
                </div>
                <p>
                  Filtered angular-speed magnitude, adaptive height, prominence,
                  and minimum peak separation.
                </p>
                {showConfig && (
                  <div className="detector-fields">
                    {[
                      {
                        key: "cutoff_hz" as const,
                        label: "Cutoff Hz",
                        step: 0.5,
                      },
                      {
                        key: "threshold_rad_s" as const,
                        label: "Height rad/s",
                        step: 0.5,
                      },
                      {
                        key: "prominence_rad_s" as const,
                        label: "Prominence rad/s",
                        step: 0.1,
                      },
                      {
                        key: "min_separation_s" as const,
                        label: "Separation s",
                        step: 0.05,
                      },
                    ].map((f) => (
                      <label className="field" key={f.key}>
                        {f.label}
                        <input
                          type="number"
                          step={f.step}
                          min=".01"
                          value={config[f.key]}
                          onChange={(e) =>
                            setConfig({
                              ...config,
                              [f.key]: Number(e.target.value),
                            })
                          }
                        />
                      </label>
                    ))}
                  </div>
                )}
                <div className="baseline-footer">
                  <span className="mono">imu_gyro_peak / v1.0.0</span>
                  <button
                    className="button primary"
                    disabled={!sensor || !!busy || run?.status === "queued"}
                    onClick={analyze}
                  >
                    <Play size={13} />
                    {busy === "analyze" || run?.status === "queued"
                      ? "Processing…"
                      : "Run baseline"}
                  </button>
                </div>
                <small>
                  Signal events are unvalidated movement proxies. No trained
                  classifier or accuracy claim.
                </small>
              </section>
            </div>
            <div className="quality-footnote">
              <div>
                <FileVideo size={14} />
                <span>
                  {sensor
                    ? `${sensor.samples.toLocaleString()} input samples · ${numeric(sensor.quality.missing_values)} missing channel values · ${Array.isArray(sensor.quality.gaps) ? sensor.quality.gaps.length : 0} timestamp gaps`
                    : "No sensor quality assessment available"}
                </span>
              </div>
              <Link href="/docs">
                Understand the method <ArrowUpRight size={13} />
              </Link>
            </div>
          </>
        )}
      </div>
    </Shell>
  );
}
