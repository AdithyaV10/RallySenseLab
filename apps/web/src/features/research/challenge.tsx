"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  ScanLine,
  Layers3,
  Play,
  FlaskConical,
  ArrowRight,
  RotateCcw,
} from "lucide-react";
import { api, SessionDetail, provenanceLabel } from "@/lib/api";
import { Badge, ErrorBox } from "@/components/ui";
import {
  Experiment,
  ExperimentRequest,
  Reference,
  LabelSet,
  modeUnavailable,
  record,
  modeOf,
} from "./types";
import { ReferenceManager } from "./reference-manager";
import { ResultComparison } from "./results";

export function Challenge({
  session,
  onSeek,
  refreshSession,
}: {
  session: SessionDetail;
  onSeek: (t: number) => void;
  refreshSession: () => void;
}) {
  const query = useQueryClient();
  const router = useRouter();
  const [mode, setMode] = useState<ExperimentRequest["mode"]>("imu");
  const [sensorId, setSensorId] = useState("");
  const [poseId, setPoseId] = useState("");
  const [syncId, setSyncId] = useState("");
  const sensors = session.sensors.filter(
    (s) =>
      s.status === "ready" &&
      Array.isArray(s.mapping.gyroscope) &&
      s.mapping.gyroscope.length === 3,
  );
  const poses = session.poses.filter((p) => p.status === "ready");
  const sensor = sensors.find((s) => s.id === sensorId) || sensors[0];
  const pose = poses.find((p) => p.id === poseId) || poses.at(-1);
  const syncs = session.syncs.filter((s) => s.sensor_id === sensor?.id);
  const sync = syncs.find((s) => s.id === syncId) || syncs.at(-1);
  const [name, setName] = useState("Baseline observation");
  const [question, setQuestion] = useState(
    "How stable are movement observations across modalities and degraded inputs?",
  );
  const [referenceId, setReferenceId] = useState("");
  const [comparison, setComparison] =
    useState<ExperimentRequest["comparison"]>("exact");
  const [hypothesis, setHypothesis] = useState("");
  const [alignment, setAlignment] = useState("");
  const [paired, setPaired] = useState(false);
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(
    Math.max(
      ...session.sensors.map((s) => s.duration_us / 1e6),
      ...session.videos.map((v) => v.duration_us / 1e6),
      1,
    ),
  );
  const [tolerance, setTolerance] = useState(150);
  const [agreement, setAgreement] = useState(150);
  const [imuThreshold, setImuThreshold] = useState(1);
  const [videoThreshold, setVideoThreshold] = useState(1);
  const [cutoff, setCutoff] = useState(8);
  const [prominence, setProminence] = useState(0.5);
  const [separation, setSeparation] = useState(0.3);
  const [adaptiveK, setAdaptiveK] = useState(3);
  const [condition, setCondition] = useState("clean");
  const [severity, setSeverity] = useState(0.2);
  const [seed, setSeed] = useState(42);
  const [windowStart, setWindowStart] = useState(1.5);
  const [selected, setSelected] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const base = `/sessions/${session.id}`;
  const history = useQuery({
    queryKey: ["experiments", session.id],
    queryFn: () => api<Experiment[]>(`${base}/experiments`),
    refetchInterval: 2000,
  });
  const refs = useQuery({
    queryKey: ["references", session.id],
    queryFn: () => api<Reference[]>(`${base}/references`),
  });
  const sets = useQuery({
    queryKey: ["label-sets", session.id],
    queryFn: () => api<LabelSet[]>(`${base}/annotation-sets`),
  });
  const reference = refs.data?.find((r) => r.id === referenceId);
  const generated = reference?.manifest.provenance === "synthetic";
  async function refresh() {
    await Promise.all([
      query.invalidateQueries({ queryKey: ["experiments", session.id] }),
      query.invalidateQueries({ queryKey: ["references", session.id] }),
      query.invalidateQueries({ queryKey: ["label-sets", session.id] }),
    ]);
    refreshSession();
  }
  async function action(fn: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await fn();
      await refresh();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  const unavailable = modeUnavailable(
    mode,
    !!sensor,
    !!pose,
    session.dataset_kind,
  );
  const runSelected = (history.data || []).filter((r) =>
    selected.includes(r.id),
  );
  const displayed = runSelected.length
    ? runSelected.slice(0, 3)
    : (history.data || []).slice(0, 1);
  const corrupt: NonNullable<ExperimentRequest["corruption"]> = {
    seed,
    dropout_fraction: 0,
    gyro_noise_sd: 0,
    acceleration_noise_sd: 0,
    timestamp_jitter_fraction: 0,
    imu_gap_start_s: 0,
    imu_gap_duration_s: 0,
    occlusion_start_s: 0,
    occlusion_duration_s: 0,
    sync_error_us: 0,
  };
  if (condition === "dropout") corrupt.dropout_fraction = severity;
  if (condition === "noise") corrupt.gyro_noise_sd = severity;
  if (condition === "acceleration_noise")
    corrupt.acceleration_noise_sd = severity;
  if (condition === "jitter") corrupt.timestamp_jitter_fraction = severity;
  if (condition === "gap") {
    corrupt.imu_gap_start_s = windowStart;
    corrupt.imu_gap_duration_s = severity;
  }
  if (condition === "occlusion") {
    corrupt.occlusion_start_s = windowStart;
    corrupt.occlusion_duration_s = severity;
  }
  if (condition === "sync") corrupt.sync_error_us = Math.round(severity * 1e6);
  async function run() {
    const payload: ExperimentRequest = {
      name,
      research_question: question,
      mode,
      sensor_id: mode === "video" ? undefined : sensor?.id,
      pose_id: mode === "imu" ? undefined : pose?.id,
      sync_id: mode === "video" ? undefined : sync?.id,
      reference_id: referenceId || undefined,
      imu: {
        cutoff_hz: cutoff,
        threshold_rad_s: imuThreshold,
        prominence_rad_s: prominence,
        min_separation_s: separation,
        adaptive_k: adaptiveK,
      },
      video: {
        threshold: videoThreshold,
        prominence,
        min_separation_s: separation,
        visibility: 0.5,
        max_gap_s: 0.15,
        adaptive_k: adaptiveK,
        smooth_window_s: 0.15,
      },
      start_us: Math.round(start * 1e6),
      end_us: Math.round(end * 1e6),
      tolerance_us: Math.round(tolerance * 1000),
      association_tolerance_us: Math.round(agreement * 1000),
      comparison: generated ? "synthetic_fixture" : comparison,
      hypothesis,
      alignment_note: alignment,
      pairing: paired
        ? session.dataset_kind === "synthetic"
          ? "synthetic_fixture"
          : "same_recording"
        : "unpaired",
      corruption: corrupt,
      force_rerun: false,
    };
    await action(async () => {
      const result = await api<Experiment>(`${base}/experiments`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setSelected((old) =>
        [result.id, ...old.filter((id) => id !== result.id)].slice(0, 3),
      );
    });
  }
  return (
    <div className="research-workspace">
      <div className="research-actions">
        <span className="research-evidence">
          No paired tennis recordings? Explore the generated software fixture.
        </span>
        <button
          className="button secondary"
          disabled={busy}
          onClick={() =>
            action(async () => {
              const demo = await api<{ id: string }>(
                "/research-demo-sessions",
                { method: "POST" },
              );
              router.push(`/sessions/${demo.id}?tab=research`);
            })
          }
        >
          Open paired synthetic lab
        </button>
      </div>
      <section className="research-hero">
        <div>
          <div className="eyebrow">
            <FlaskConical size={14} /> SENSOR FUSION CHALLENGE
          </div>
          <h2>
            Three perspectives.
            <br />
            <span>One testable question.</span>
          </h2>
          <p>
            Measure what each modality sees. Freeze the evidence. Challenge the
            assumptions.
          </p>
        </div>
        <div className="research-hero-note">
          <Badge tone={session.dataset_kind === "recorded" ? "teal" : "amber"}>
            {provenanceLabel(session.dataset_kind)}
          </Badge>
          <p>
            {session.dataset_kind === "synthetic"
              ? "Generated signals test software, not tennis performance."
              : session.dataset_kind === "mixed"
                ? "Unrelated sources. Inspect each modality; paired fusion is disabled."
                : "Recorded inputs. Pairing and label independence require your documented verification."}
          </p>
          <span>NO CALIBRATED CONFIDENCE · NO IMPACT CLAIM</span>
        </div>
      </section>
      <div className="research-modes" role="group" aria-label="Inference mode">
        {[
          {
            key: "video" as const,
            title: "Video only",
            icon: ScanLine,
            kicker: "A / VISUAL",
            text: "Torso-relative wrist speed from stored pose observations.",
          },
          {
            key: "imu" as const,
            title: "IMU only",
            icon: Activity,
            kicker: "B / INERTIAL",
            text: "Angular-speed peaks, movement windows and sample quality.",
          },
          {
            key: "fusion" as const,
            title: "Multimodal fusion",
            icon: Layers3,
            kicker: "C / ASSOCIATION",
            text: "One-to-one temporal association with both source times retained.",
          },
        ].map((m) => {
          const reason = modeUnavailable(
            m.key,
            !!sensor,
            !!pose,
            session.dataset_kind,
          );
          return (
            <button
              key={m.key}
              className={`research-mode ${mode === m.key ? "selected" : ""}`}
              aria-pressed={mode === m.key}
              disabled={!!reason}
              onClick={() => {
                setMode(m.key);
                setCondition("clean");
              }}
            >
              <span>
                {m.kicker}
                <m.icon size={23} />
              </span>
              <h3>{m.title}</h3>
              <p>{reason || m.text}</p>
              <small>
                {reason
                  ? "INPUT REQUIRED"
                  : mode === m.key
                    ? "SELECTED"
                    : "SELECT MODE"}
                <ArrowRight size={14} />
              </small>
            </button>
          );
        })}
      </div>
      <ErrorBox error={error || history.error || refs.error || sets.error} />
      <section className="panel research-setup">
        <div className="panel-heading">
          <h3>Experiment setup</h3>
          <Badge>{mode.toUpperCase()} / VERSIONED BASELINE</Badge>
        </div>
        <div className="research-fields">
          <label className="field">
            Run name
            <input
              aria-label="Experiment name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
          <label className="field">
            Frozen reference
            <select
              aria-label="Frozen reference"
              value={referenceId}
              onChange={(e) => setReferenceId(e.target.value)}
            >
              <option value="">No reference — inference only</option>
              {refs.data?.map((r) => (
                <option key={r.id} value={r.id}>
                  {String(r.manifest.set_name)} · r{r.revision} ·{" "}
                  {String(r.manifest.event_type)}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            Artificial condition
            <select
              aria-label="Artificial condition"
              value={condition}
              onChange={(e) => {
                setCondition(e.target.value);
                setSeverity(0.2);
              }}
            >
              <option value="clean">Clean observations</option>
              <option value="dropout" disabled={mode === "video"}>
                Missing IMU samples
              </option>
              <option value="noise" disabled={mode === "video"}>
                Gyroscope noise
              </option>
              <option value="acceleration_noise" disabled={mode === "video"}>
                Acceleration noise
              </option>
              <option value="jitter" disabled={mode === "video"}>
                Timestamp irregularity
              </option>
              <option value="gap" disabled={mode === "video"}>
                IMU missing window
              </option>
              <option value="occlusion" disabled={mode === "imu"}>
                Wrist landmark occlusion
              </option>
              <option value="sync" disabled={mode === "video"}>
                Incorrect synchronization
              </option>
            </select>
          </label>
        </div>
        {condition !== "clean" && (
          <div className="research-corruption">
            <div>
              <strong>Controlled perturbation</strong>
              <p>
                Applied to a derived in-memory copy. Original measurements and
                references stay intact.
              </p>
            </div>
            <label className="field">
              {condition === "dropout" || condition === "jitter"
                ? "Fraction"
                : condition === "noise"
                  ? "Noise SD (rad/s)"
                  : condition === "acceleration_noise"
                    ? "Noise SD (m/s²)"
                    : "Duration / offset (s)"}
              <input
                aria-label="Corruption severity"
                type="number"
                step=".05"
                min={condition === "sync" ? -10 : 0}
                max={
                  condition === "dropout"
                    ? 0.95
                    : condition === "jitter"
                      ? 0.45
                      : 100
                }
                value={severity}
                onChange={(e) => setSeverity(Number(e.target.value))}
              />
            </label>
            <label className="field">
              Random seed
              <input
                type="number"
                value={seed}
                min="0"
                onChange={(e) => setSeed(Number(e.target.value))}
              />
            </label>
            {["occlusion", "gap"].includes(condition) && (
              <label className="field">
                Window start (s)
                <input
                  type="number"
                  min="0"
                  value={windowStart}
                  onChange={(e) => setWindowStart(Number(e.target.value))}
                />
              </label>
            )}
          </div>
        )}
        <details className="research-config">
          <summary>Inputs, timing & algorithm parameters</summary>
          <div className="research-fields">
            <label className="field">
              Sensor
              <select
                aria-label="Research sensor"
                value={sensor?.id || ""}
                disabled={mode === "video"}
                onChange={(e) => setSensorId(e.target.value)}
              >
                {sensors.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              Stored pose
              <select
                aria-label="Research pose"
                value={pose?.id || ""}
                disabled={mode === "imu"}
                onChange={(e) => setPoseId(e.target.value)}
              >
                {poses.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.id.slice(0, 8)} · {String(p.quality.processed_frames)}{" "}
                    frames
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              Alignment revision
              <select
                value={sync?.id || ""}
                disabled={mode === "video"}
                onChange={(e) => setSyncId(e.target.value)}
              >
                {syncs.map((s) => (
                  <option key={s.id} value={s.id}>
                    r{s.revision} · {(s.offset_us / 1e6).toFixed(3)} s
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="research-fields compact">
            {[
              ["Start (s)", start, setStart],
              ["End (s)", end, setEnd],
              ["Evaluation tolerance (ms)", tolerance, setTolerance],
              ["Association gate (ms)", agreement, setAgreement],
              ["IMU height (rad/s)", imuThreshold, setImuThreshold],
              ["Video speed (torso/s)", videoThreshold, setVideoThreshold],
              ["IMU cutoff (Hz)", cutoff, setCutoff],
              ["Peak prominence", prominence, setProminence],
              ["Adaptive threshold k", adaptiveK, setAdaptiveK],
              ["Minimum separation (s)", separation, setSeparation],
            ].map(([label, value, setter]) => (
              <label className="field" key={String(label)}>
                {String(label)}
                <input
                  type="number"
                  step="any"
                  min="0"
                  value={Number(value)}
                  onChange={(e) =>
                    (setter as (n: number) => void)(Number(e.target.value))
                  }
                />
              </label>
            ))}
          </div>
          <label className="field">
            Research question
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </label>
        </details>
        {mode === "fusion" && (
          <div className="research-fields">
            <label className="check-label">
              <input
                type="checkbox"
                checked={paired}
                onChange={(e) => setPaired(e.target.checked)}
              />{" "}
              These modalities observe the same recording / generated fixture
            </label>
            <label className="field">
              Independent alignment evidence
              <textarea
                aria-label="Alignment evidence"
                value={alignment}
                onChange={(e) => setAlignment(e.target.value)}
                placeholder="Cue times, placement, offset sign, and residual uncertainty."
              />
            </label>
          </div>
        )}
        {reference && !generated && (
          <div className="research-fields">
            <label className="field">
              Comparison semantics
              <select
                aria-label="Comparison semantics"
                value={comparison}
                onChange={(e) =>
                  setComparison(
                    e.target.value as ExperimentRequest["comparison"],
                  )
                }
              >
                <option value="exact">
                  Require identical event definition
                </option>
                <option value="proxy_hypothesis">
                  Explicit proxy-to-reference hypothesis
                </option>
              </select>
            </label>
            {comparison === "proxy_hypothesis" && (
              <label className="field">
                Hypothesis
                <textarea
                  aria-label="Proxy hypothesis"
                  value={hypothesis}
                  onChange={(e) => setHypothesis(e.target.value)}
                  placeholder="Explain why this measured peak might estimate the labeled event; this is unvalidated."
                />
              </label>
            )}
          </div>
        )}
        {generated && (
          <p className="research-notice">
            Generated references: metrics will be labeled synthetic software
            verification, never real-world accuracy.
          </p>
        )}
        <div className="research-actions">
          <p>
            {unavailable ||
              "Immutable run · explicit alignment · deterministic processing"}
          </p>
          <button
            className="button primary"
            disabled={
              busy ||
              !!unavailable ||
              (mode === "fusion" && (!paired || alignment.trim().length < 8))
            }
            onClick={run}
          >
            <Play size={14} />
            {busy ? "Submitting…" : "Run experiment"}
          </button>
        </div>
      </section>
      <ReferenceManager
        busy={busy}
        session={session}
        sets={sets.data || []}
        references={refs.data || []}
        refresh={refresh}
        action={action}
      />
      <div className="research-section-heading">
        <div>
          <div className="eyebrow">MEASURED RESULTS</div>
          <h2>Evidence, side by side.</h2>
        </div>
        <span>Select up to three runs to compare.</span>
      </div>
      {!!history.data?.length && (
        <div className="research-history">
          {history.data.map((run) => (
            <div className="research-history-row" key={run.id}>
              <label>
                <input
                  type="checkbox"
                  checked={displayed.some((r) => r.id === run.id)}
                  onChange={(e) =>
                    setSelected((old) =>
                      e.target.checked
                        ? [run.id, ...old].slice(0, 3)
                        : old.filter((id) => id !== run.id),
                    )
                  }
                />
                <span>
                  {run.name}
                  <small>
                    {modeOf(run)} ·{" "}
                    {new Date(run.created_at).toLocaleTimeString()} ·{" "}
                    {String(record(run.manifest.request).comparison)}
                  </small>
                </span>
              </label>
              <Badge
                tone={
                  run.status === "failed"
                    ? "red"
                    : run.status === "succeeded"
                      ? "teal"
                      : "neutral"
                }
              >
                {run.status}
              </Badge>
              <button
                className="icon-button"
                title="Rerun frozen configuration"
                aria-label={`Rerun ${run.name}`}
                disabled={busy}
                onClick={() =>
                  action(async () => {
                    const next = await api<Experiment>(`${base}/experiments`, {
                      method: "POST",
                      body: JSON.stringify({
                        ...record(run.manifest.request),
                        force_rerun: true,
                      }),
                    });
                    setSelected([next.id, run.id]);
                  })
                }
              >
                <RotateCcw size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
      <ResultComparison runs={displayed} onSeek={onSeek} />
      <footer className="research-footer">
        Visibility measures observability. Strength measures a signal. Accuracy
        requires independent labels. None is calibrated model confidence.
      </footer>
    </div>
  );
}
