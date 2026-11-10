import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Braces,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  Download,
  Fingerprint,
  FlaskConical,
  Layers,
  Menu,
  Pause,
  Play,
  ScanLine,
  ShieldCheck,
  X,
} from "lucide-react";
import type { Dataset, Experiment } from "./data";
import {
  asset,
  clampTime,
  description,
  modalitySignal,
  modeName,
  nearestFrame,
  percent,
  seconds,
  validateDataset,
} from "./data";
import { Pose, Signal } from "./visuals";
import "./style.css";

function Brand() {
  return (
    <a href="#/" className="brand" aria-label="RallySense Lab home">
      <span className="brand-icon">
        <Activity size={22} />
      </span>
      RallySense <span>LAB</span>
    </a>
  );
}
function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="tag">
      <span />
      {children}
    </span>
  );
}
function App() {
  const [data, setData] = useState<Dataset>();
  const [error, setError] = useState("");
  const [hash, setHash] = useState(window.location.hash || "#/");
  const [menu, setMenu] = useState(false);
  const [time, setTime] = useState(0);
  const [experimentId, setExperimentId] = useState("");
  useEffect(() => {
    const abort = new AbortController();
    fetch(asset("data/showcase.json"), { signal: abort.signal })
      .then((r) => {
        if (!r.ok)
          throw new Error("The synthetic snapshot is temporarily unavailable.");
        return r.json();
      })
      .then((v) => {
        const d = validateDataset(v);
        setData(d);
        setExperimentId(
          d.experiments.find((e) => e.name.startsWith("Clean fusion"))!.id,
        );
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => abort.abort();
  }, []);
  useEffect(() => {
    const change = () => {
      setHash(window.location.hash || "#/");
      setMenu(false);
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  const path = hash.slice(1).split("?")[0];
  const experiment = data?.experiments.find((e) => e.id === experimentId);
  const jump = (us: number) => {
    setTime(clampTime(us, data!.duration_us));
    window.location.hash = "/replay";
  };
  return (
    <>
      <a
        className="skip"
        href="#main"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById("main")?.focus();
        }}
      >
        Skip to content
      </a>
      <header className="header">
        <Brand />
        <button
          className="menu-toggle icon"
          aria-label={menu ? "Close navigation" : "Open navigation"}
          onClick={() => setMenu(!menu)}
        >
          {menu ? <X /> : <Menu />}
        </button>
        <nav
          className={menu ? "navigation open" : "navigation"}
          aria-label="Main navigation"
        >
          {[
            ["/replay", "Observatory"],
            ["/challenge", "Sensor Fusion Challenge"],
            ["/compare", "Compare"],
            ["/methodology", "Methodology"],
          ].map(([href, label]) => (
            <a
              key={href}
              href={`#${href}`}
              aria-current={path === href ? "page" : undefined}
            >
              {label}
            </a>
          ))}
          <span className="header-note">
            <i />
            Interactive showcase
          </span>
        </nav>
      </header>
      <main id="main" tabIndex={-1}>
        {error ? (
          <div className="status-page">
            <FlaskConical />
            <h1>Snapshot unavailable</h1>
            <p role="alert">{error}</p>
            <button className="button" onClick={() => window.location.reload()}>
              Retry loading
            </button>
          </div>
        ) : !data || !experiment ? (
          <div className="status-page" role="status">
            <Activity className="loading-icon" />
            <h1>Opening the observatory</h1>
            <p>Loading the reviewed synthetic snapshot…</p>
          </div>
        ) : path === "/" || path === "" ? (
          <Landing data={data} />
        ) : path === "/methodology" ? (
          <Methodology data={data} />
        ) : path.startsWith("/report/") ? (
          <Report data={data} id={path.split("/")[2]} />
        ) : ["/replay", "/challenge", "/compare"].includes(path) ? (
          <div className="workspace">
            <div className="workspace-intro">
              <div>
                <div className="eyebrow">
                  <FlaskConical size={13} />
                  THE SYNTHETIC OBSERVATORY <span>/</span> EXPERIMENT 01
                </div>
                <h1>
                  Paired motion. <em>Shared questions.</em>
                </h1>
                <p>
                  Generated motion, sparse measurements, and evidence you can
                  inspect.
                </p>
              </div>
              <Tag>Synthetic data only</Tag>
            </div>
            <div className="workspace-tabs">
              <a href="#/replay" className={path === "/replay" ? "active" : ""}>
                <Activity size={15} />
                Synchronized replay
              </a>
              <a
                href="#/challenge"
                className={path === "/challenge" ? "active" : ""}
              >
                <Layers size={15} />
                Sensor Fusion Challenge
              </a>
              <a
                href="#/compare"
                className={path === "/compare" ? "active" : ""}
              >
                <Braces size={15} />
                Experiment comparison
              </a>
              <span>STORED RESULTS · NO LIVE INFERENCE</span>
            </div>
            {path === "/replay" ? (
              <Replay data={data} time={time} setTime={setTime} />
            ) : path === "/challenge" ? (
              <Challenge
                data={data}
                experiment={experiment}
                select={setExperimentId}
                jump={jump}
              />
            ) : (
              <Comparison data={data} />
            )}
            <div className="truth-strip">
              <ShieldCheck size={16} />
              <span>
                Software observations, not validated tennis accuracy. Uploads
                and new inference are available only in the preserved private
                research platform.
              </span>
            </div>
          </div>
        ) : (
          <div className="status-page">
            <h1>This view isn’t in the snapshot.</h1>
            <a className="button" href="#/replay">
              Open the observatory <ArrowRight size={16} />
            </a>
          </div>
        )}
      </main>
      <footer className="footer">
        <Brand />
        <span>Observations first. Evidence follows.</span>
        <a href="#/methodology">
          Scope & provenance <ArrowUpRight size={13} />
        </a>
        <a href={asset("NOTICES.txt")}>Third-party notices</a>
      </footer>
    </>
  );
}

function Landing({ data }: { data: Dataset }) {
  const clean = data.experiments.find((e) =>
    e.name.startsWith("Clean fusion"),
  )!;
  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">
            <i className="live-dot" /> A MOVEMENT RESEARCH LAB
          </div>
          <h1>
            Movement.
            <br />
            <em>Measured.</em>
            <br />
            Questioned.
          </h1>
          <p className="hero-description">
            What can sparse signals tell us about movement?
            <br className="desktop-break" /> Explore the moments where inertial
            measurements
            <br className="desktop-break" /> and visual observations agree. And
            where they don’t.
          </p>
          <div className="hero-actions">
            <a className="button primary" href="#/replay">
              Explore Interactive Demo <ArrowUpRight size={18} />
            </a>
            <a className="text-link" href="#/methodology">
              Read the methodology <ArrowRight size={15} />
            </a>
          </div>
          <p className="hero-disclosure">
            <ShieldCheck size={14} />
            Generated fixtures. Precomputed results. No athlete accuracy claim.
          </p>
        </div>
        <a
          className="hero-visual"
          href="#/replay"
          aria-label="Explore the synchronized synthetic movement replay"
        >
          <div className="visual-top">
            <span>
              <i />
              PAIRED MOTION / SYNTHETIC
            </span>
            <ScanLine size={17} />
          </div>
          <Pose hero frame={nearestFrame(data.pose.frames, 2000000)} />
          <div className="observation-note">
            <span className="small-label">OBSERVATION 01</span>
            <strong>
              Two signals.
              <br />
              One shared clock.
            </strong>
            <span className="note-coordinate">
              t = 2.000 s · generated reference
            </span>
          </div>
          <div className="hero-signal">
            <Signal
              points={modalitySignal(clean, "imu")}
              time={2000000}
              duration={data.duration_us}
              label="ANGULAR SPEED"
              unit="rad/s"
            />
            <div className="visual-caption">
              <span>100 Hz IMU · analytical pose</span>
              <span className="round-arrow">
                <ArrowUpRight size={16} />
              </span>
            </div>
          </div>
        </a>
      </section>
      <div className="spec-strip">
        <div>
          <span>01 / OBSERVE</span>
          <strong>Sparse inertial signals</strong>
        </div>
        <div>
          <span>02 / ALIGN</span>
          <strong>One explicit timeline</strong>
        </div>
        <div>
          <span>03 / CHALLENGE</span>
          <strong>Inspect the failures</strong>
        </div>
        <div className="spec-link">
          <a href="#/challenge">
            Enter the Sensor Fusion Challenge <ArrowRight size={19} />
          </a>
        </div>
      </div>
      <section className="question-section">
        <div className="eyebrow">ENGINEERED FOR INSPECTION</div>
        <div className="section-heading">
          <h2>
            Agreement is useful.
            <br />
            <em>Understanding is better.</em>
          </h2>
          <p>
            A polished result is only the beginning. Trace each observation to
            its source, change the stored scenario, and discover what happens
            when the evidence goes missing.
          </p>
        </div>
        <div className="feature-grid">
          {[
            [
              Activity,
              "The signal",
              "Inspect angular-speed samples and measured signal peaks. A peak is an observation, not a confirmed swing.",
            ],
            [
              ScanLine,
              "The observation",
              "Replay generated video alongside stored analytical landmarks. No MediaPipe model runs in this showcase.",
            ],
            [
              Layers,
              "The association",
              "Compare unlike events on a known clock. Temporal agreement tests a hypothesis; it doesn’t prove an impact.",
            ],
          ].map(([Icon, title, text]) => {
            const I = Icon as typeof Activity;
            return (
              <article key={String(title)}>
                <I size={24} />
                <h3>{String(title)}</h3>
                <p>{String(text)}</p>
                <a href="#/challenge">
                  Inspect the evidence <ArrowUpRight size={15} />
                </a>
              </article>
            );
          })}
        </div>
      </section>
      <section className="engineering-banner">
        <div>
          <div className="eyebrow">
            A SNAPSHOT OF THE FULL RESEARCH PLATFORM
          </div>
          <h2>
            Built to preserve
            <br />
            <em>the path to a result.</em>
          </h2>
        </div>
        <div>
          <p>
            The preserved platform combines Next.js, FastAPI, PostgreSQL,
            durable jobs, real browser MediaPipe extraction and immutable
            research manifests. This public experience is a separate, fully
            static React + TypeScript showcase.
          </p>
          <div className="tech-tags">
            <span>React</span>
            <span>TypeScript</span>
            <span>Timestamped signals</span>
            <span>Frozen provenance</span>
          </div>
          <a className="text-link" href="#/methodology">
            How the research works <ArrowRight size={15} />
          </a>
        </div>
      </section>
    </div>
  );
}

function Replay({
  data,
  time,
  setTime,
}: {
  data: Dataset;
  time: number;
  setTime: (us: number) => void;
}) {
  const video = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [zoom, setZoom] = useState(false);
  const [rate, setRate] = useState("1");
  const [mediaError, setMediaError] = useState(false);
  const query = new URLSearchParams(window.location.hash.split("?")[1]);
  const initialTime = useRef(
    query.has("t")
      ? clampTime(Number(query.get("t")) * 1e6, data.duration_us)
      : time,
  );
  const clean = data.experiments.find((e) =>
    e.name.startsWith("Clean fusion"),
  )!;
  const frame = nearestFrame(data.pose.frames, time);
  const seek = (us: number) => {
    const t = clampTime(us, data.duration_us);
    setTime(t);
    if (video.current && video.current.readyState >= 1)
      video.current.currentTime = t / 1e6;
  };
  useEffect(() => {
    if (!playing) return;
    let id: number;
    const tick = () => {
      if (video.current)
        setTime(clampTime(video.current.currentTime * 1e6, data.duration_us));
      id = requestAnimationFrame(tick);
    };
    id = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(id);
  }, [playing, setTime, data.duration_us]);
  const toggle = async () => {
    if (!video.current) return;
    if (playing) video.current.pause();
    else {
      try {
        await video.current.play();
        setMediaError(false);
      } catch {
        setMediaError(true);
      }
    }
  };
  const active = clean.result.events.find(
    (e) => Math.abs(e.t_session_us - time) <= 150000,
  );
  return (
    <>
      <div className="replay-heading">
        <div>
          <h2>
            Follow the motion.<span> Question the signal.</span>
          </h2>
          <p>
            Play, scrub, or select a measured event to inspect the same moment
            across observations.
          </p>
        </div>
        <a href="#/challenge" className="text-link">
          Challenge this observation <ArrowRight size={16} />
        </a>
      </div>
      <div className="replay-grid">
        <section className="panel media-panel">
          <div className="panel-title">
            <span>
              <i className="live-dot" />
              GENERATED MOVEMENT VIDEO
            </span>
            <span>
              MP4 · {data.video.width} × {data.video.height}
            </span>
          </div>
          <div className="video-stage">
            <video
              ref={video}
              src={asset(`data/${data.video.file}`)}
              muted
              playsInline
              preload="auto"
              aria-label="Generated stick figure movement video"
              onLoadedMetadata={() => {
                if (video.current) {
                  video.current.currentTime = initialTime.current / 1e6;
                  setTime(initialTime.current);
                }
              }}
              onPlay={() => setPlaying(true)}
              onPause={() => setPlaying(false)}
              onEnded={() => {
                setPlaying(false);
                setTime(data.duration_us);
              }}
              onSeeked={() => {
                if (video.current) setTime(video.current.currentTime * 1e6);
              }}
              onError={() => setMediaError(true)}
            />
            <span className="media-label">
              SYNTHETIC FIXTURE · NOT ATHLETE FOOTAGE
            </span>
            <div className="video-time">{seconds(time, 3)}</div>
          </div>
          {mediaError && (
            <p role="alert" className="warning">
              Video playback is unavailable. You can still scrub the stored
              observations below.
            </p>
          )}
          <div className="video-foot">
            <span>Known generated clock</span>
            <span>{(data.duration_us / 1e6).toFixed(1)} s source window</span>
          </div>
        </section>
        <section className="panel pose-panel">
          <div className="panel-title">
            <span>STORED POSE OBSERVATIONS</span>
            <span className="mint">30 Hz target</span>
          </div>
          <Pose frame={frame} />
          <div className="pose-foot">
            <span>
              Analytical landmarks <strong>Not MediaPipe output</strong>
            </span>
            <span className="mono">{seconds(frame.t_video_us, 3)}</span>
          </div>
        </section>
      </div>
      <section className="panel timeline-panel">
        <div className="transport">
          <button
            className="play-button"
            aria-label={playing ? "Pause replay" : "Play replay"}
            onClick={toggle}
          >
            {playing ? <Pause size={19} /> : <Play size={19} />}
          </button>
          <button
            className="icon"
            aria-label="Seek backward 0.1 seconds"
            onClick={() => seek(time - 100000)}
          >
            <ChevronLeft size={18} />
          </button>
          <button
            className="icon"
            aria-label="Seek forward 0.1 seconds"
            onClick={() => seek(time + 100000)}
          >
            <ChevronRight size={18} />
          </button>
          <output className="time-output" data-testid="shared-time">
            {seconds(time, 3)}
            <span> / {seconds(data.duration_us, 1)}</span>
          </output>
          <div className="transport-spacer" />
          <label className="rate">
            Playback speed
            <select
              aria-label="Playback speed"
              value={rate}
              onChange={(e) => {
                setRate(e.target.value);
                if (video.current)
                  video.current.playbackRate = Number(e.target.value);
              }}
            >
              <option value="0.5">0.5×</option>
              <option value="1">1×</option>
              <option value="1.5">1.5×</option>
            </select>
          </label>
          <button
            className={`zoom ${zoom ? "selected" : ""}`}
            aria-pressed={zoom}
            onClick={() => setZoom(!zoom)}
          >
            {zoom ? "Show full trace" : "Zoom to 2 s"}
          </button>
        </div>
        <div className="scrubber">
          <input
            type="range"
            min="0"
            max={data.duration_us}
            step="10000"
            value={time}
            aria-label="Shared session timeline"
            onChange={(e) => seek(Number(e.target.value))}
          />
          <div className="scrubber-events">
            {clean.result.events.map((e, i) => (
              <button
                key={i}
                style={{
                  left: `${(e.t_session_us / data.duration_us) * 100}%`,
                }}
                aria-label={`Seek to measured event ${i + 1} at ${seconds(e.t_session_us)}`}
                title={`Measured angular-speed event · ${seconds(e.t_session_us)}`}
                onClick={() => seek(e.t_session_us)}
              />
            ))}
          </div>
          <div className="scrubber-labels">
            <span>0.0 s</span>
            <span>Shared session clock · microsecond timestamps</span>
            <span>{seconds(data.duration_us, 1)}</span>
          </div>
        </div>
        <Signal
          points={modalitySignal(clean, "imu")}
          time={time}
          duration={data.duration_us}
          label="IMU · angular-speed magnitude"
          unit="rad/s"
          zoom={zoom}
          events={clean.result.components!.imu!.events}
          references={data.reference.events}
          onSeek={seek}
        />
        <Signal
          points={modalitySignal(clean, "video")}
          time={time}
          duration={data.duration_us}
          label="Visual · torso-relative wrist speed"
          unit="torso lengths/s"
          color="var(--violet)"
          zoom={zoom}
          events={clean.result.components!.video!.events}
          references={data.reference.events}
          onSeek={seek}
        />
        <div className="signal-legend">
          <span>
            <i className="legend-cursor" />
            Shared cursor
          </span>
          <span>
            <i className="legend-reference" />
            Generated reference
          </span>
          <span>Each trace has its own labeled scale.</span>
        </div>
      </section>
      <div className="replay-bottom">
        <section className="panel event-card">
          <div className="small-label">CURRENT OBSERVATION</div>
          <h3>
            {active
              ? "Signals meet in time."
              : "Inspect the space between events."}
          </h3>
          <p>
            {active
              ? `The stored association anchors to IMU time ${seconds(active.imu_time_us!)}. The visual observation differs by ${(active.disagreement_us! / 1000).toFixed(3)} ms.`
              : "Select an event marker at 2 or 5 seconds. Angular speed and image wrist speed measure different things."}
          </p>
          <span className="mini-note">
            Temporal association does not confirm a physical tennis event.
          </span>
        </section>
        <section className="panel source-card">
          <Fingerprint size={21} />
          <div>
            <h3>Small dataset. Full traceability.</h3>
            <p>
              {data.sensor.samples.length} IMU samples ·{" "}
              {data.pose.frames.length} stored pose frames · shared generated
              clock.
            </p>
            <a href="#/methodology" className="text-link">
              Inspect provenance <ArrowUpRight size={14} />
            </a>
          </div>
        </section>
      </div>
    </>
  );
}

function Metrics({ experiment }: { experiment: Experiment }) {
  const e = experiment.result.evaluation;
  return (
    <>
      <div className="metrics">
        {[
          ["Precision", e?.precision],
          ["Recall", e?.recall],
          ["F1", e?.f1],
        ].map(([label, value]) => (
          <div key={String(label)}>
            <span>{label}</span>
            <strong>{percent(value as number | undefined)}</strong>
          </div>
        ))}
      </div>
      {e ? (
        <div className="counts">
          <span>
            TP <b>{e.tp}</b>
          </span>
          <span>
            FP <b>{e.fp}</b>
          </span>
          <span>
            FN <b>{e.fn}</b>
          </span>
          <span>
            Tolerance <b>{e.tolerance_us / 1000} ms</b>
          </span>
        </div>
      ) : (
        <p className="mini-note">
          {experiment.status === "failed"
            ? "Inference failed: no valid result to score."
            : "No scoring reference selected for this stored run."}
        </p>
      )}
      <p className="metric-disclosure">
        Synthetic software verification — not real-world model accuracy. “—”
        means undefined or unavailable.
      </p>
    </>
  );
}
function Challenge({
  data,
  experiment,
  select,
  jump,
}: {
  data: Dataset;
  experiment: Experiment;
  select: (id: string) => void;
  jump: (us: number) => void;
}) {
  const e = experiment.result.evaluation;
  return (
    <>
      <div className="challenge-heading">
        <div className="eyebrow">SENSOR FUSION CHALLENGE</div>
        <h2>
          Three perspectives.
          <br />
          <em>One testable question.</em>
        </h2>
        <p>
          Change the stored experiment. See which observations survive missing
          data and a misaligned clock.
        </p>
      </div>
      <div className="mode-grid">
        {(
          [
            [
              "video",
              ScanLine,
              "Torso-relative wrist speed from stored analytical landmarks.",
            ],
            [
              "imu",
              Activity,
              "Angular-speed peaks from the generated inertial signal.",
            ],
            [
              "fusion",
              Layers,
              "One-to-one temporal association, keeping both source times.",
            ],
          ] as const
        ).map(([mode, Icon, text]) => (
          <button
            key={mode}
            className={`mode-card ${experiment.mode === mode ? "selected" : ""}`}
            onClick={() =>
              select(
                data.experiments.find(
                  (e) => e.mode === mode && e.name.startsWith("Clean"),
                )!.id,
              )
            }
          >
            <span className="small-label">
              {mode === "video"
                ? "A / VISUAL"
                : mode === "imu"
                  ? "B / INERTIAL"
                  : "C / ASSOCIATION"}
              <Icon size={20} />
            </span>
            <h3>{modeName(mode)}</h3>
            <p>{text}</p>
            <span className="mode-action">
              Open clean stored result <ArrowUpRight size={15} />
            </span>
          </button>
        ))}
      </div>
      <section className="panel scenario">
        <div>
          <span className="small-label">PRECOMPUTED SCENARIO</span>
          <label htmlFor="scenario">Choose the evidence</label>
        </div>
        <select
          id="scenario"
          value={experiment.id}
          onChange={(event) => select(event.target.value)}
        >
          {data.experiments.map((e) => (
            <option key={e.id} value={e.id}>
              {e.name} · {modeName(e.mode)}
            </option>
          ))}
        </select>
        <span className="stored-badge">
          <Check size={13} />
          Stored result
        </span>
        <p>
          {description(experiment)}{" "}
          <strong>Selection never starts a new inference job.</strong>
        </p>
      </section>
      <div className="results-grid">
        <section className="panel result-main">
          <div className="panel-title">
            <span>
              {modeName(experiment.mode).toUpperCase()} /{" "}
              {experiment.status.toUpperCase()}
            </span>
            <span className="mono">{experiment.id.slice(0, 8)}</span>
          </div>
          <div className="result-title">
            <h3>{experiment.name.split(" / ")[0]}</h3>
            <code>{experiment.algorithm}</code>
          </div>
          {experiment.status === "failed" ? (
            <div className="failure-state">
              <CircleHelp size={30} />
              <h3>No valid observation to infer from.</h3>
              <p>
                This stored full-occlusion experiment failed explicitly. It is
                not a zero-error or successful model result.
              </p>
              <code>{experiment.result.failure_code}</code>
            </div>
          ) : (
            <>
              <div className="result-events">
                <strong>{experiment.result.events.length}</strong>
                <span>
                  computed signal events
                  <br />
                  <small>precomputed from synthetic observations</small>
                </span>
              </div>
              <Signal
                points={modalitySignal(experiment, "imu")}
                time={2000000}
                duration={data.duration_us}
                label="Stored IMU observations"
                unit="rad/s"
                events={experiment.result.components?.imu?.events}
                references={e ? data.reference.events : []}
                onSeek={jump}
              />
              <Signal
                points={modalitySignal(experiment, "video")}
                time={2000000}
                duration={data.duration_us}
                label="Stored visual observations"
                unit="torso lengths/s"
                color="var(--violet)"
                events={experiment.result.components?.video?.events}
                references={e ? data.reference.events : []}
                onSeek={jump}
              />
            </>
          )}
          <div className="result-links">
            <a className="button secondary" href={`#/report/${experiment.id}`}>
              Open experiment report <ArrowUpRight size={15} />
            </a>
            <a
              href={asset(`reports/${experiment.id}.json`)}
              download
              className="text-link"
            >
              <Download size={14} />
              JSON
            </a>
          </div>
        </section>
        <aside className="result-aside">
          <section className="panel evaluation">
            <div className="small-label">GENERATED REFERENCE MATCHING</div>
            <Metrics experiment={experiment} />
            {e && (
              <p className="mini-note">
                Reference independence: <b>false</b>. Clean pulse centers come
                from the same analytical generator.
              </p>
            )}
          </section>
          <section className="panel interpretation">
            <div className="small-label">READ THIS RESULT</div>
            <h3>
              {experiment.status === "failed"
                ? "Failure is evidence, too."
                : e && e.fn
                  ? "Missing evidence stays missing."
                  : "Agreement needs a definition."}
            </h3>
            <p>{description(experiment)}</p>
            <p>
              Signal strength is not confidence. Matching a generated pulse does
              not validate a swing detector.
            </p>
            <a href="#/compare" className="text-link">
              Compare stored results <ArrowRight size={15} />
            </a>
          </section>
        </aside>
      </div>
      <section className="panel failure-explorer">
        <div className="explorer-heading">
          <div>
            <div className="small-label">FAILURE EXPLORER</div>
            <h3>Return to the moment.</h3>
          </div>
          <span>Links seek the original generated replay.</span>
        </div>
        {!e ? (
          <p className="mini-note">
            No evaluation match list is defined for this run. Its stored result
            remains available in the report.
          </p>
        ) : (
          <div className="failure-grid">
            <div>
              <h4>
                Matched references <span>{e.matches.length}</span>
              </h4>
              {e.matches.length ? (
                e.matches.map((m, i) => (
                  <button
                    className="event-link"
                    key={i}
                    onClick={() => jump(m.reference_us)}
                  >
                    <span>
                      <Check size={14} />
                      Reference at {seconds(m.reference_us)}
                    </span>
                    <span>
                      {(m.signed_error_us / 1000).toFixed(3)} ms{" "}
                      <ArrowUpRight size={14} />
                    </span>
                  </button>
                ))
              ) : (
                <p>No stored matches.</p>
              )}
            </div>
            <div>
              <h4>
                Missed references <span>{e.missed_references.length}</span>
              </h4>
              {e.missed_references.length ? (
                e.missed_references.map((i) => (
                  <button
                    className="event-link missed"
                    key={i}
                    onClick={() => jump(data.reference.events[i].t_session_us)}
                  >
                    <span>Missed reference #{i + 1}</span>
                    <span>
                      {seconds(data.reference.events[i].t_session_us)}{" "}
                      <ArrowUpRight size={14} />
                    </span>
                  </button>
                ))
              ) : (
                <p>No missed generated references.</p>
              )}
            </div>
            <div>
              <h4>
                Unmatched predictions{" "}
                <span>{e.unmatched_predictions.length}</span>
              </h4>
              {e.unmatched_predictions.length ? (
                e.unmatched_predictions.map((i) => (
                  <button
                    className="event-link"
                    key={i}
                    onClick={() =>
                      jump(experiment.result.events[i].t_session_us)
                    }
                  >
                    {seconds(experiment.result.events[i].t_session_us)}
                    <ArrowUpRight size={14} />
                  </button>
                ))
              ) : (
                <p>No unmatched output events.</p>
              )}
            </div>
          </div>
        )}
        <details>
          <summary>Timing disagreements & unassociated observations</summary>
          <div className="scroll-table">
            <table>
              <thead>
                <tr>
                  <th>IMU time</th>
                  <th>Visual time</th>
                  <th>Visual − IMU</th>
                </tr>
              </thead>
              <tbody>
                {experiment.result.events
                  ?.filter((v) => v.imu_time_us !== undefined)
                  .map((v, i) => (
                    <tr key={i}>
                      <td>{seconds(v.imu_time_us!, 6)}</td>
                      <td>{seconds(v.video_time_us!, 6)}</td>
                      <td>{(v.disagreement_us! / 1000).toFixed(3)} ms</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
          {(["imu", "video"] as const).map((mode) => (
            <div key={mode} className="unmatched-modality">
              <span>{modeName(mode)} unassociated candidates:</span>
              {(
                experiment.result.quality?.[
                  mode === "imu" ? "unmatched_imu" : "unmatched_video"
                ] ?? []
              ).map((i) => {
                const event = experiment.result.components?.[mode]?.events[i];
                return event ? (
                  <button
                    className="text-link"
                    key={i}
                    onClick={() => jump(event.t_session_us)}
                  >
                    {seconds(event.t_session_us)} <ArrowUpRight size={12} />
                  </button>
                ) : null;
              })}
              <span className="mini-note">
                See stored JSON for complete modality quality.
              </span>
            </div>
          ))}
          <p className="mini-note">
            Association preserves the IMU anchor. Cross-modality timing
            differences are distinct from generated-reference scoring errors.
          </p>
        </details>
      </section>
    </>
  );
}

function Comparison({ data }: { data: Dataset }) {
  const [ids, setIds] = useState(
    data.experiments
      .filter(
        (e) =>
          e.name.startsWith("Clean IMU") ||
          e.name.startsWith("Clean fusion") ||
          e.name.startsWith("Offset"),
      )
      .map((e) => e.id),
  );
  const selected = data.experiments.filter((e) => ids.includes(e.id));
  return (
    <>
      <div className="comparison-heading">
        <div className="eyebrow">EXPERIMENT COMPARISON</div>
        <h2>
          Evidence,<em> side by side.</em>
        </h2>
        <p>
          Select up to three actual stored results. Every number retains its
          original definition and provenance.
        </p>
      </div>
      <div className="comparison-layout">
        <section className="panel selection">
          <h3>
            Stored experiments <span>{ids.length} / 3</span>
          </h3>
          {data.experiments.map((e) => (
            <label key={e.id} className={ids.includes(e.id) ? "checked" : ""}>
              <input
                type="checkbox"
                aria-label={`Compare ${e.name}`}
                checked={ids.includes(e.id)}
                disabled={ids.length === 3 && !ids.includes(e.id)}
                onChange={() =>
                  setIds(
                    ids.includes(e.id)
                      ? ids.filter((id) => id !== e.id)
                      : [...ids, e.id],
                  )
                }
              />
              <span>
                {e.name.split(" / ")[0]}
                <small>
                  {modeName(e.mode)} · {e.status}
                </small>
              </span>
            </label>
          ))}
        </section>
        <div className="comparison-results">
          {selected.length ? (
            <>
              <section className="panel comparison-table">
                <div className="panel-title">
                  ACTUAL STORED EVALUATIONS <span>SYNTHETIC ONLY</span>
                </div>
                <div className="scroll-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Observation</th>
                        {selected.map((e) => (
                          <th key={e.id}>
                            {e.name.split(" / ")[0]}
                            <small>{modeName(e.mode)}</small>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        "Events",
                        "Precision",
                        "Recall",
                        "F1",
                        "TP / FP / FN",
                        "Mean absolute reference error",
                        "Eligible coverage",
                      ].map((label, i) => (
                        <tr key={label}>
                          <th>{label}</th>
                          {selected.map((e) => {
                            const v = e.result.evaluation;
                            return (
                              <td key={e.id}>
                                {i === 0
                                  ? e.status === "failed"
                                    ? "Unavailable"
                                    : e.result.events.length
                                  : i < 4
                                    ? percent(
                                        v?.[
                                          (
                                            [
                                              "precision",
                                              "recall",
                                              "f1",
                                            ] as const
                                          )[i - 1]
                                        ],
                                      )
                                    : i === 4
                                      ? v
                                        ? `${v.tp} / ${v.fp} / ${v.fn}`
                                        : "—"
                                      : i === 5
                                        ? v?.mean_absolute_error_us == null
                                          ? "—"
                                          : `${(v.mean_absolute_error_us / 1000).toFixed(3)} ms`
                                        : percent(e.result.coverage?.fraction)}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="metric-disclosure">
                  Undefined metrics stay undefined. Generated references are
                  non-independent; these scores do not measure tennis accuracy.
                </p>
              </section>
              <section className="panel event-lanes">
                <div className="small-label">
                  COMPUTED EVENT TIMES / SHARED GENERATED CLOCK
                </div>
                {selected.map((e) => (
                  <div key={e.id}>
                    <span>{e.name.split(" / ")[0]}</span>
                    <div className="event-lane">
                      {data.reference.events.map((r, i) => (
                        <i
                          key={i}
                          style={{
                            left: `${(r.t_session_us / data.duration_us) * 100}%`,
                          }}
                        />
                      ))}
                      {e.result.events?.map((v, i) => (
                        <a
                          key={i}
                          style={{
                            left: `${(v.t_session_us / data.duration_us) * 100}%`,
                          }}
                          href={`#/replay?t=${v.t_session_us / 1e6}`}
                          aria-label={`${e.name} event at ${seconds(v.t_session_us)}`}
                          title={seconds(v.t_session_us)}
                        />
                      ))}
                      {e.status === "failed" && (
                        <span>Inference failed — no event result</span>
                      )}
                    </div>
                  </div>
                ))}
                <div className="lane-labels">
                  <span>0.0 s</span>
                  <span>Amber ticks: generated references</span>
                  <span>8.0 s</span>
                </div>
              </section>
              <div className="comparison-reports">
                {selected.map((e) => (
                  <a key={e.id} href={`#/report/${e.id}`} className="panel">
                    <Fingerprint size={19} />
                    <span>
                      {e.name.split(" / ")[0]}
                      <small>Inspect immutable snapshot & export</small>
                    </span>
                    <ArrowUpRight size={17} />
                  </a>
                ))}
              </div>
            </>
          ) : (
            <div className="panel empty-selection">
              <Layers size={30} />
              <h3>Choose your comparison.</h3>
              <p>
                Select a stored experiment on the left to inspect its evidence.
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function Report({ data, id }: { data: Dataset; id: string }) {
  const e = data.experiments.find((e) => e.id === id);
  if (!e)
    return (
      <div className="status-page">
        <h1>Report not found</h1>
        <a href="#/compare">Choose a stored experiment</a>
      </div>
    );
  return (
    <article className="report">
      <div className="report-actions">
        <a href="#/compare">
          <ChevronLeft size={15} />
          Back to comparison
        </a>
        <button className="button secondary" onClick={() => window.print()}>
          Print / Save PDF
        </button>
        <a
          className="button primary"
          href={asset(`reports/${e.id}.md`)}
          download
        >
          <Download size={15} />
          Download Markdown
        </a>
        <a className="text-link" href={asset(`reports/${e.id}.json`)} download>
          JSON <Download size={14} />
        </a>
      </div>
      <div className="eyebrow">RALLYSENSE LAB / EXPERIMENT RECORD</div>
      <h1>{e.name}</h1>
      <Tag>Synthetic software verification</Tag>
      <p className="report-deck">
        Actual precomputed result from reviewed generated observations. Not
        real-world athlete accuracy.
      </p>
      <dl className="report-meta">
        <div>
          <dt>Mode</dt>
          <dd>{modeName(e.mode)}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{e.status}</dd>
        </div>
        <div>
          <dt>Algorithm</dt>
          <dd>{e.algorithm}</dd>
        </div>
        <div>
          <dt>Experiment ID</dt>
          <dd>{e.id}</dd>
        </div>
      </dl>
      <section>
        <h2>Computed observations</h2>
        <Metrics experiment={e} />
        <p>{description(e)}</p>
        {e.status === "failed" && (
          <p className="warning">
            Explicit inference failure: {e.result.failure_code}. No successful
            result or metrics are implied.
          </p>
        )}
        <div className="scroll-table">
          <table>
            <thead>
              <tr>
                <th>Event</th>
                <th>Session time</th>
                <th>Definition</th>
                <th>Visual − IMU</th>
              </tr>
            </thead>
            <tbody>
              {e.result.events?.map((v, i) => (
                <tr key={i}>
                  <td>{i + 1}</td>
                  <td>{seconds(v.t_session_us, 6)}</td>
                  <td>{v.event_type}</td>
                  <td>
                    {v.disagreement_us == null
                      ? "—"
                      : `${(v.disagreement_us / 1000).toFixed(3)} ms`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section>
        <h2>Quality, pairing & limitations</h2>
        {(e.result.limitations ?? data.limitations).map((l) => (
          <p key={l}>{l}</p>
        ))}
        <p>
          Frozen generated reference: independence <strong>false</strong>.{" "}
          {data.reference.manifest.definition}
        </p>
        <p>
          Offset-only synchronization does not estimate clock drift. Signal
          agreement does not confirm swings, ball contact or biomechanical
          reconstruction.
        </p>
      </section>
      <section>
        <h2>Source & reproducibility</h2>
        <p>
          Source release <code>{data.source_release}</code>. All input artifacts
          were hash-verified during export. No private database or recording was
          used.
        </p>
        <details>
          <summary>Inspect the frozen configuration and hashes</summary>
          <pre>
            {JSON.stringify(
              {
                fingerprint: e.fingerprint,
                request: e.request,
                runtime: e.runtime,
                dependency_lock_sha256: e.dependency_lock_sha256,
                implementation_sha256: e.implementation_sha256,
                sources: data.sources,
              },
              null,
              2,
            )}
          </pre>
        </details>
      </section>
      <p className="report-end">
        This static report preserves a computed research record. Changing pages
        does not execute a model.
      </p>
    </article>
  );
}

function Methodology({ data }: { data: Dataset }) {
  return (
    <article className="methodology">
      <div className="eyebrow">METHODS / SCOPE / PROVENANCE</div>
      <h1>
        Make the observation.
        <br />
        <em>Keep the uncertainty.</em>
      </h1>
      <p className="method-deck">
        RallySense Lab studies what sparse inertial and visual signals can
        reveal about tennis-related movement. This showcase makes the
        engineering inspectable without pretending the experiment is real-world
        validation.
      </p>
      <div className="method-columns">
        <aside>
          <a href="#/replay">
            <Activity size={16} />
            Explore replay
          </a>
          <a href="#/challenge">
            <FlaskConical size={16} />
            Challenge the evidence
          </a>
          <a href={asset("data/provenance.json")} download>
            <Fingerprint size={16} />
            Download provenance
          </a>
          <a href={asset("NOTICES.txt")}>
            <Braces size={16} />
            Third-party notices
          </a>
        </aside>
        <div>
          {[
            [
              "01",
              "Measured signal events",
              "The offline IMU pipeline normalizes channels to SI units, preserves missing intervals, filters angular-speed magnitude, and detects peaks with explicit settings. A gyro peak is a measured signal event or an unvalidated proxy. It is not automatically a confirmed tennis swing or impact.",
            ],
            [
              "02",
              "Visual observations",
              "The full research platform supports actual browser MediaPipe pose extraction. This static snapshot instead contains generated analytical landmarks on a known trajectory, aligned with the generated stick-figure video. No model weights, MediaPipe runtime or browser extraction are shipped. Stored wrist speed is image-space speed normalized by torso scale, with gaps retained.",
            ],
            [
              "03",
              "Temporal association",
              "IMU and visual observations are matched one-to-one within a declared temporal interval. Both timestamps remain visible; the output keeps its IMU anchor. Unlike event definitions are not silently averaged. Correlation in time supports investigation, not a shared physical-event or causal claim.",
            ],
            [
              "04",
              "Evaluation that keeps its denominator",
              "Evaluation uses a frozen reference, a declared interval and a cardinality/timing-error matching objective. Precision, recall and F1 remain unavailable when their definitions require missing denominators. Missing observations retain reference misses. The reference here comes from the same generator: independence is false. Clean scores demonstrate software behavior, not athlete accuracy.",
            ],
            [
              "05",
              "Failure is part of the product",
              "Precomputed cases include an IMU gap, wrist occlusion, a one-second alignment error and a full-occlusion inference failure. The visitor selects an existing stored result. No new prediction, inference job or dataset mutation occurs in the browser. The failure explorer links back to the original generated source timeline; it does not manufacture missing observations.",
            ],
            [
              "06",
              "A static window into a full-stack lab",
              "The preserved private platform uses Next.js, FastAPI, PostgreSQL, persistent artifacts, durable workers, annotation revisioning, synchronization and immutable input manifests. This separate Vite / React / TypeScript application requires only static assets. Uploads, capture, new inference and annotation editing are deliberately absent.",
            ],
          ].map(([n, title, body]) => (
            <section key={n}>
              <span className="method-number">{n}</span>
              <h2>{title}</h2>
              <p>{body}</p>
            </section>
          ))}
          <section>
            <div className="small-label">THIS EXACT SNAPSHOT</div>
            <h2>Trace the source.</h2>
            <p>
              {data.sensor.samples.length} source IMU samples,{" "}
              {data.pose.frames.length} analytical pose frames,{" "}
              {data.experiments.length} stored experiments. Every displayed
              evaluation comes directly from those stored results.
            </p>
            <p>
              Source checkpoint: <code>{data.source_release}</code>
            </p>
            <ul>
              {data.sources.map((s) => (
                <li key={s.sha256}>
                  <strong>{s.kind}</strong>
                  <code>{s.sha256}</code>
                </li>
              ))}
            </ul>
            <p>
              No private recordings, backend credentials, native executables,
              model weights or external fonts are included. The generated video
              and illustration were created for this project; required runtime
              library notices are included.
            </p>
            <a className="button primary" href="#/replay">
              Explore the evidence <ArrowRight size={16} />
            </a>
          </section>
        </div>
      </div>
    </article>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
