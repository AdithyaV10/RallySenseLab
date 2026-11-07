"use client";
import { useRef, useState } from "react";
import {
  Upload,
  FileVideo,
  FileSpreadsheet,
  Check,
  ArrowUpRight,
  RefreshCw,
} from "lucide-react";
import { api, SessionDetail, SensorMapping } from "@/lib/api";
import { Badge, ErrorBox, Modal } from "@/components/ui";
import { useCapabilities } from "@/lib/capabilities";

export function DataManager({
  session,
  refresh,
}: {
  session: SessionDetail;
  refresh: () => void;
}) {
  const readonly = useCapabilities().data?.mode === "demo_readonly";
  const [allJobs, setAllJobs] = useState(false);
  const videoInput = useRef<HTMLInputElement>(null),
    sensorInput = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState<unknown>(null),
    [csv, setCsv] = useState<File | null>(null),
    [headers, setHeaders] = useState<string[]>([]);
  const [videoProvenance, setVideoProvenance] = useState<
    "recorded" | "synthetic"
  >("recorded");
  const [timestamp, setTimestamp] = useState("timestamp_s"),
    [acc, setAcc] = useState("ax_m_s2,ay_m_s2,az_m_s2"),
    [gyro, setGyro] = useState("gx_rad_s,gy_rad_s,gz_rad_s"),
    [placement, setPlacement] = useState("unknown");
  const [provenance, setProvenance] = useState<"recorded" | "synthetic">(
    session.dataset_kind === "synthetic" ? "synthetic" : "recorded",
  );
  const [timeUnit, setTimeUnit] = useState<"s" | "ms" | "us">("s"),
    [accUnit, setAccUnit] = useState<"m/s2" | "g">("m/s2"),
    [gyroUnit, setGyroUnit] = useState<"rad/s" | "deg/s">("rad/s"),
    [accKind, setAccKind] = useState<
      "linear" | "including_gravity" | "unknown"
    >("unknown"),
    [delimiter, setDelimiter] = useState<"," | ";" | "\t">(",");
  async function uploadVideo(file?: File) {
    if (!file || readonly) return;
    setBusy(true);
    setError(null);
    try {
      if (file.size > 500 * 1024 * 1024)
        throw new Error("Video exceeds 500 MiB");
      const form = new FormData();
      form.set("file", file);
      form.set("metadata", JSON.stringify({ provenance: videoProvenance }));
      await api(`/sessions/${session.id}/videos`, {
        method: "POST",
        body: form,
      });
      refresh();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
      if (videoInput.current) videoInput.current.value = "";
    }
  }
  async function selectCsv(file?: File) {
    if (!file || readonly) return;
    setError(null);
    if (file.size > 50 * 1024 * 1024) {
      setError(new Error("CSV exceeds 50 MiB"));
      return;
    }
    const firstLine = (await file.slice(0, 8192).text())
      .split(/\r?\n/)[0]
      .replace(/^\uFEFF/, "");
    const separator = firstLine.includes(";")
      ? ";"
      : firstLine.includes("\t")
        ? "\t"
        : ",";
    setDelimiter(separator);
    const cols = firstLine
      .split(separator)
      .map((s) => s.replace(/^"|"$/g, "").trim());
    setHeaders(cols);
    setTimestamp(cols.find((c) => /time/i.test(c)) || cols[0]);
    setAcc(cols.filter((c) => /^a[xyz]_/.test(c)).join(","));
    setGyro(cols.filter((c) => /^g[xyz]_/.test(c)).join(","));
    setCsv(file);
    if (sensorInput.current) sensorInput.current.value = "";
  }
  async function importCsv(e: React.FormEvent) {
    e.preventDefault();
    if (!csv || readonly) return;
    setBusy(true);
    setError(null);
    try {
      const mapping: SensorMapping = {
        provenance,
        timestamp,
        time_unit: timeUnit,
        acceleration: acc ? acc.split(",").map((s) => s.trim()) : [],
        gyroscope: gyro ? gyro.split(",").map((s) => s.trim()) : [],
        acceleration_unit: accUnit,
        gyroscope_unit: gyroUnit,
        acceleration_kind: accKind,
        delimiter,
        placement,
      };
      const form = new FormData();
      form.set("file", csv);
      form.set("mapping", JSON.stringify(mapping));
      await api(`/sessions/${session.id}/sensor-imports`, {
        method: "POST",
        body: form,
      });
      setCsv(null);
      refresh();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="data-manager">
      <label className="field">
        Video source provenance
        <select
          aria-label="Video source provenance"
          value={videoProvenance}
          onChange={(e) =>
            setVideoProvenance(e.target.value as typeof videoProvenance)
          }
        >
          <option value="recorded">Recorded video</option>
          <option value="synthetic">Generated software fixture</option>
        </select>
      </label>
      <div className="data-intro">
        <h2>Build your observation set.</h2>
        <p>
          Import a video and sensor measurements. Each source keeps its original
          clock, units, and provenance.
        </p>
      </div>
      <ErrorBox error={!csv ? error : null} />
      <div className="upload-grid">
        <button
          className="upload-zone"
          disabled={readonly || busy}
          onClick={() => videoInput.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            uploadVideo(e.dataTransfer.files[0]);
          }}
        >
          <span className="upload-symbol">
            <FileVideo size={25} />
          </span>
          <h3>Add a movement video</h3>
          <p>Drop a file here, or browse your recordings.</p>
          <small>MP4 H.264 / WEBM · MAX 500 MIB · 10 MIN</small>
          <span className="button secondary">
            <Upload size={15} />
            Choose video
          </span>
        </button>
        <button
          className="upload-zone"
          disabled={readonly || busy}
          onClick={() => sensorInput.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            selectCsv(e.dataTransfer.files[0]);
          }}
        >
          <span className="upload-symbol amber">
            <FileSpreadsheet size={25} />
          </span>
          <h3>Import motion measurements</h3>
          <p>Map accelerometer and gyroscope CSV columns.</p>
          <small>CANONICAL / EXTRACTED PHYPHOX CSV · MAX 50 MIB</small>
          <span className="button secondary">
            <Upload size={15} />
            Choose sensor CSV
          </span>
        </button>
      </div>
      <input
        ref={videoInput}
        aria-label="Video file"
        type="file"
        hidden
        accept=".mp4,.webm"
        onChange={(e) => uploadVideo(e.target.files?.[0])}
      />
      <input
        ref={sensorInput}
        aria-label="Sensor CSV file"
        type="file"
        hidden
        accept=".csv"
        onChange={(e) => selectCsv(e.target.files?.[0])}
      />
      {busy && (
        <div className="loading">
          <RefreshCw className="spin" size={16} />
          Transferring file…
        </div>
      )}
      <div className="panel">
        <div className="panel-heading">
          <h3>Source inventory</h3>
          <Badge>{session.videos.length + session.sensors.length} assets</Badge>
        </div>
        {[
          ...session.videos.map((v) => ({
            id: v.id,
            name: v.name,
            status: v.status,
            kind: "video",
          })),
          ...session.sensors.map((s) => ({
            id: s.id,
            name: s.name,
            status: s.status,
            kind: "sensor",
          })),
        ].map((item) => (
          <div className="asset-row" key={item.id}>
            {item.kind === "video" ? (
              <FileVideo size={18} />
            ) : (
              <FileSpreadsheet size={18} />
            )}
            <div>
              <strong>{item.name}</strong>
              <small>
                {item.kind.toUpperCase()} · {item.id.slice(0, 8)}
              </small>
            </div>
            <Badge
              tone={
                item.status === "ready"
                  ? "teal"
                  : item.status === "failed"
                    ? "red"
                    : "neutral"
              }
            >
              {item.status === "ready" ? <Check size={11} /> : null}
              {item.status}
            </Badge>
          </div>
        ))}
        {!session.videos.length && !session.sensors.length && (
          <p className="empty-text">
            Your source inventory will appear here after the first upload.
          </p>
        )}
      </div>
      <div className="panel">
        <div className="panel-heading">
          <h3>Processing activity</h3>
          <span className="muted">Durable local jobs</span>
        </div>
        {session.jobs
          .slice()
          .reverse()
          .slice(0, allJobs ? session.jobs.length : 8)
          .map((job) => (
            <div className="job-row" key={job.id}>
              <div>
                <strong>{job.kind.replaceAll("_", " ")}</strong>
                <small>
                  {job.error ||
                    `Attempt ${job.attempt} · ${job.id.slice(0, 8)}`}
                </small>
              </div>
              <Badge
                tone={
                  job.state === "succeeded"
                    ? "teal"
                    : job.state === "failed"
                      ? "red"
                      : "neutral"
                }
              >
                {job.state}
              </Badge>
            </div>
          ))}
        {session.jobs.length > 8 && (
          <button
            className="button ghost small"
            onClick={() => setAllJobs(!allJobs)}
          >
            {allJobs
              ? "Show recent jobs"
              : `Show all ${session.jobs.length} jobs`}
          </button>
        )}
        {!session.jobs.length && (
          <p className="empty-text">No processing jobs yet.</p>
        )}
      </div>
      <Modal
        open={!!csv}
        onOpenChange={(v) => {
          if (!v) setCsv(null);
        }}
        title="Map your measurements"
        description={`${csv?.name} · Choose exact columns and units before importing.`}
      >
        <form onSubmit={importCsv} className="mapping-form">
          <div className="column-preview">HEADERS: {headers.join(" / ")}</div>
          <div className="form-grid">
            <label className="field">
              TIMESTAMP COLUMN
              <input
                required
                value={timestamp}
                onChange={(e) => setTimestamp(e.target.value)}
              />
            </label>
            <label className="field">
              TIME UNIT
              <select
                value={timeUnit}
                onChange={(e) => setTimeUnit(e.target.value as typeof timeUnit)}
              >
                <option value="s">Seconds</option>
                <option value="ms">Milliseconds</option>
                <option value="us">Microseconds</option>
              </select>
            </label>
          </div>
          <label className="field">
            ACCELERATION X, Y, Z COLUMNS (EMPTY IF ABSENT)
            <input value={acc} onChange={(e) => setAcc(e.target.value)} />
          </label>
          <label className="field">
            GYROSCOPE X, Y, Z COLUMNS (EMPTY IF ABSENT)
            <input value={gyro} onChange={(e) => setGyro(e.target.value)} />
          </label>
          <div className="form-grid">
            <label className="field">
              ACCELERATION UNIT
              <select
                value={accUnit}
                onChange={(e) => setAccUnit(e.target.value as typeof accUnit)}
              >
                <option value="m/s2">m/s²</option>
                <option value="g">g</option>
              </select>
            </label>
            <label className="field">
              ANGULAR RATE UNIT
              <select
                value={gyroUnit}
                onChange={(e) => setGyroUnit(e.target.value as typeof gyroUnit)}
              >
                <option value="rad/s">rad/s</option>
                <option value="deg/s">deg/s</option>
              </select>
            </label>
          </div>
          <label className="field">
            ACCELERATION INCLUDES
            <select
              value={accKind}
              onChange={(e) => setAccKind(e.target.value as typeof accKind)}
            >
              <option value="unknown">Unknown gravity handling</option>
              <option value="including_gravity">Gravity included</option>
              <option value="linear">
                Linear acceleration (gravity removed)
              </option>
            </select>
          </label>
          <label className="field">
            SENSOR PLACEMENT
            <input
              value={placement}
              onChange={(e) => setPlacement(e.target.value)}
              placeholder="e.g. secured wrist / unknown"
            />
          </label>
          <label className="field">
            MEASUREMENT ORIGIN
            <select
              aria-label="Measurement origin"
              value={provenance}
              onChange={(e) =>
                setProvenance(e.target.value as typeof provenance)
              }
            >
              <option value="recorded">Recorded sensor observations</option>
              <option value="synthetic">
                Generated synthetic measurements
              </option>
            </select>
          </label>
          <p className="form-note">
            CSV streams retain their own timestamps. Ingest separate phyphox
            exports individually; rows are never joined by index.
          </p>
          <ErrorBox error={error} />
          <button className="button primary" disabled={readonly || busy}>
            {busy ? "Importing…" : "Import and normalize"}
            <ArrowUpRight size={15} />
          </button>
        </form>
      </Modal>
    </div>
  );
}
