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
import { DemoGuide } from "./demo-guide";
import { useCapabilities } from "@/lib/capabilities";
import type { LabelSet } from "@/features/research/types";
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
  const capabilities = useCapabilities();
  const readonly = capabilities.data?.mode === "demo_readonly";
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
  const [samplingMethod, setSamplingMethod] = useState<
    "playback" | "seek_backpressure"
  >("playback");
  const [zoomUs, setZoomUs] = useState(0),
    [markers, setMarkers] = useState(true);
  const cursor = useRef(0);
  const playbackEnd = useRef<number | null>(null);
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
  const labelSets = useQuery({
    queryKey: ["label-sets", id],
    queryFn: () => api<LabelSet[]>(`/sessions/${id}/annotation-sets`),
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
  const sourceStart = zoomUs
    ? Math.floor(timeUs / zoomUs) * zoomUs - offsetUs
    : 0;
  const sourceEnd = zoomUs
    ? (Math.floor(timeUs / zoomUs) + 1) * zoomUs - offsetUs
    : 1_200_000_000;
  const samples = useQuery({
    queryKey: [
      "samples",
      sensor?.id,
      sync?.id,
      offsetUs,
      zoomUs,
      zoomUs ? Math.floor(timeUs / zoomUs) : 0,
    ],
    queryFn: () =>
      sourceEnd < 0 || sourceStart > (sensor?.duration_us || 0)
        ? Promise.resolve({
            clock: "source_relative_us" as const,
            source_count: 0,
            returned_count: 0,
            data: [],
          })
        : api<Samples>(
            `/sensor-recordings/${sensor!.id}/samples?start_us=${Math.max(0, sourceStart)}&end_us=${Math.max(1, sourceEnd)}`,
          ),
    enabled: !!sensor,
    staleTime: Infinity,
  });
  const frames = useQuery({
    queryKey: ["pose", pose?.id, Math.floor(timeUs / 2e6)],
    queryFn: () =>
      api<{ frames: PoseFrame[]; truncated: boolean }>(
        `/pose-tracks/${pose!.id}/frames?start_us=${Math.max(0, Math.floor(timeUs / 2e6) * 2e6 - 2e6)}&end_us=${Math.floor(timeUs / 2e6) * 2e6 + 4e6}&max_frames=2000`,
      ),
    enabled: !!pose,
    staleTime: Infinity,
    gcTime: 60_000,
  });
  const durationUs = Number(
    video?.duration_us ||
      Math.max(0, (sensor?.duration_us || 0) + offsetUs) ||
      18e6,
  );
  const refresh = useCallback(() => {
    query.invalidateQueries({ queryKey: ["session", id] });
    query.invalidateQueries({ queryKey: ["label-sets", id] });
  }, [query, id]);
  const seek = useCallback(
    (t: number) => {
      playbackEnd.current = null;
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
        if (playbackEnd.current !== null && next >= playbackEnd.current) {
          playbackEnd.current = null;
          setPlaying(false);
        }
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
      if (readonly)
        throw new Error(
          "This demonstration is read-only. Inspect existing results or use a private local workspace to run new experiments.",
        );
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
  useEffect(() => {
    const timer = setTimeout(() => {
      try {
        const prefs = JSON.parse(
          localStorage.getItem(`rallysense-view-${id}`) || "{}",
        );
        if (typeof prefs.axes === "boolean") setAxes(prefs.axes);
        if (typeof prefs.markers === "boolean") setMarkers(prefs.markers);
        if ([0.25, 0.5, 1, 1.5, 2].includes(prefs.rate)) setRate(prefs.rate);
        if ([0, 2e6, 5e6, 10e6].includes(prefs.zoomUs)) setZoomUs(prefs.zoomUs);
      } catch {
        /* A corrupt preference never blocks replay. */
      }
    }, 0);
    return () => clearTimeout(timer);
  }, [id]);
  function remember(update: Record<string, number | boolean>) {
    try {
      localStorage.setItem(
        `rallysense-view-${id}`,
        JSON.stringify({ axes, markers, rate, zoomUs, ...update }),
      );
    } catch {
      /* Storage can be disabled. */
    }
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
        {data.dataset_kind === "synthetic" && <DemoGuide onTab={setTab} />}
        {readonly && (
          <p className="research-notice">
            Read-only demonstration: replay, stored experiments and exports are
            available. Mutations are disabled.
          </p>
        )}
        <ErrorBox error={error || samples.error || frames.error} />
        {data.jobs
          .filter((j) => j.state === "failed" && j.kind !== "experiment")
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
                  onTime={(t) => {
                    setTimeUs(t);
                    if (
                      playbackEnd.current !== null &&
                      t >= playbackEnd.current
                    ) {
                      playbackEnd.current = null;
                      setPlaying(false);
                    }
                  }}
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
                      onChange={(e) => {
                        setRate(Number(e.target.value));
                        remember({ rate: Number(e.target.value) });
                      }}
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
                      markers &&
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
                <div className="replay-tools">
                  <button
                    className="button ghost small"
                    onClick={() => {
                      const center = timeUs;
                      seek(Math.max(0, center - 1e6));
                      playbackEnd.current = Math.min(durationUs, center + 1e6);
                      setPlaying(true);
                    }}
                  >
                    Replay 2 s around cursor
                  </button>
                  {pose && (
                    <>
                      <button
                        className="button ghost small"
                        disabled={
                          !frames.data?.frames.some(
                            (f) => f.t_video_us < timeUs - 1000,
                          )
                        }
                        onClick={() => {
                          setPlaying(false);
                          const f = frames.data?.frames
                            .filter((f) => f.t_video_us < timeUs - 1000)
                            .at(-1);
                          if (f) seek(f.t_video_us);
                        }}
                      >
                        Previous observed pose frame
                      </button>
                      <button
                        className="button ghost small"
                        disabled={
                          !frames.data?.frames.some(
                            (f) => f.t_video_us > timeUs + 1000,
                          )
                        }
                        onClick={() => {
                          setPlaying(false);
                          const f = frames.data?.frames.find(
                            (f) => f.t_video_us > timeUs + 1000,
                          );
                          if (f) seek(f.t_video_us);
                        }}
                      >
                        Next observed pose frame
                      </button>
                    </>
                  )}
                  <button
                    className="button ghost small"
                    onClick={() => {
                      setPlaying(false);
                      seek(timeUs - 100_000);
                    }}
                    aria-label="Step backward 100 milliseconds"
                  >
                    −100 ms
                  </button>
                  <button
                    className="button ghost small"
                    onClick={() => {
                      setPlaying(false);
                      seek(timeUs + 100_000);
                    }}
                    aria-label="Step forward 100 milliseconds"
                  >
                    +100 ms
                  </button>
                  <label>
                    Signal window
                    <select
                      aria-label="Signal zoom window"
                      value={zoomUs}
                      onChange={(e) => {
                        setZoomUs(Number(e.target.value));
                        remember({ zoomUs: Number(e.target.value) });
                      }}
                    >
                      <option value={0}>Full session</option>
                      <option value={2e6}>2 seconds</option>
                      <option value={5e6}>5 seconds</option>
                      <option value={10e6}>10 seconds</option>
                    </select>
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={markers}
                      onChange={(e) => {
                        setMarkers(e.target.checked);
                        remember({ markers: e.target.checked });
                      }}
                    />
                    Prediction markers
                  </label>
                  <span>
                    Space: play / pause · ← / →: 100 ms · Steps are time seeks,
                    not exact decoded frames.
                  </span>
                </div>
                <div className="clock-readout">
                  <span>SESSION / VIDEO {(timeUs / 1e6).toFixed(3)} s</span>
                  <span>SENSOR {((timeUs - offsetUs) / 1e6).toFixed(3)} s</span>
                  <span>
                    OFFSET {(offsetUs / 1e6).toFixed(3)} s · R
                    {sync?.revision ?? "—"}
                  </span>
                </div>
                {frames.data?.truncated && (
                  <p className="amber-text">
                    The local pose window exceeds the display limit. Inference
                    still reads the full track.
                  </p>
                )}
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
                      disabled={readonly || !!busy}
                      onChange={(e) =>
                        setPoseTarget(Number(e.target.value) as 10 | 30)
                      }
                    >
                      <option value={10}>10 Hz / standard</option>
                      <option value={30}>30 Hz / slow extraction</option>
                    </select>
                    <select
                      aria-label="Pose sampling method"
                      value={samplingMethod}
                      disabled={readonly || !!busy}
                      onChange={(e) =>
                        setSamplingMethod(
                          e.target.value as typeof samplingMethod,
                        )
                      }
                    >
                      <option value="playback">Playback sampling</option>
                      <option value="seek_backpressure">
                        Seek + processing backpressure
                      </option>
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
                        disabled={readonly || !!busy}
                        onClick={() =>
                          action("pose", async () => {
                            setPlaying(false);
                            abort.current = new AbortController();
                            await extractPose(
                              video.id,
                              setPoseMessage,
                              abort.current.signal,
                              poseTarget,
                              samplingMethod,
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
                {pose && (
                  <p className="processing-message">
                    Stored track reused for replay and inference. Achieved
                    cadence{" "}
                    {numeric(pose.quality.observed_sample_hz).toFixed(2)} Hz ·
                    largest gap{" "}
                    {(numeric(pose.quality.max_gap_us) / 1000).toFixed(1)} ms.{" "}
                    {numeric(pose.quality.max_gap_us) > 150000
                      ? "Sparse observations limit event timing."
                      : "Cadence does not establish landmark accuracy."}
                  </p>
                )}
              </div>
              <EventPanel
                sets={labelSets.data}
                readonly={readonly}
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
                    onChange={(e) => {
                      setAxes(e.target.checked);
                      remember({ axes: e.target.checked });
                    }}
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
                        durationUs={
                          zoomUs
                            ? Math.min(
                                durationUs,
                                (Math.floor(timeUs / zoomUs) + 1) * zoomUs,
                              )
                            : durationUs
                        }
                        startUs={
                          zoomUs ? Math.floor(timeUs / zoomUs) * zoomUs : 0
                        }
                        kind={p.kind}
                        axes={axes}
                        markers={
                          markers ? predictions.map((e) => e.t_session_us) : []
                        }
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
                    disabled={readonly || !sensor || !!busy}
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
                <small>
                  Existing results retain their original alignment. Offset
                  alignment does not correct drift.
                </small>
                <p>
                  Pairing evidence:{" "}
                  {String(sync?.evidence.note || "Not recorded")}.{" "}
                  {sync?.evidence.end_residual_us !== undefined &&
                    `End cue residual: ${Number(sync.evidence.end_residual_us) / 1e6} s.`}{" "}
                  <Link href="/record">
                    Record start/end cues in Collection studio.
                  </Link>
                </p>
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
                    disabled={
                      readonly || !sensor || !!busy || run?.status === "queued"
                    }
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
