"use client";
import Link from "next/link";
import { useState } from "react";
import { Check, ArrowRight } from "lucide-react";
import { api, type SessionDetail } from "@/lib/api";
import { Badge, ErrorBox } from "@/components/ui";
export function AlignmentEditor({
  session,
  refresh,
}: {
  session: SessionDetail;
  refresh: () => void;
}) {
  const sensors = session.sensors.filter((s) => s.status === "ready"),
    videos = session.videos.filter((v) => v.status === "ready");
  const [sensorId, setSensorId] = useState(""),
    [videoId, setVideoId] = useState("");
  const [startSensor, setStartSensor] = useState("0"),
    [startVideo, setStartVideo] = useState("0"),
    [endSensor, setEndSensor] = useState(""),
    [endVideo, setEndVideo] = useState(""),
    [uncertainty, setUncertainty] = useState("0.04"),
    [note, setNote] = useState(""),
    [paired, setPaired] = useState(false),
    [error, setError] = useState<unknown>(null),
    [busy, setBusy] = useState(false);
  const latest = session.syncs.toSorted((a, b) => b.revision - a.revision)[0];
  const sensor = sensorId || sensors[0]?.id,
    video = videoId || videos[0]?.id;
  const offset = Number(startVideo) - Number(startSensor),
    endResidual =
      endSensor !== "" && endVideo !== ""
        ? Number(endVideo) - Number(endSensor) - offset
        : null;
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const cues = [
        {
          sensor_us: Math.round(Number(startSensor) * 1e6),
          video_us: Math.round(Number(startVideo) * 1e6),
          uncertainty_us: Math.round(Number(uncertainty) * 1e6),
        },
      ];
      if (endSensor !== "" && endVideo !== "")
        cues.push({
          sensor_us: Math.round(Number(endSensor) * 1e6),
          video_us: Math.round(Number(endVideo) * 1e6),
          uncertainty_us: Math.round(Number(uncertainty) * 1e6),
        });
      await api(`/sessions/${session.id}/sync-configurations`, {
        method: "POST",
        body: JSON.stringify({
          sensor_id: sensor,
          video_id: video,
          offset_us: Math.round(offset * 1e6),
          evidence: { paired, note, cues },
        }),
      });
      refresh();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel capture-card">
      <div className="capture-card-title">
        <Check size={20} />
        <h2>Quality & alignment</h2>
        <Badge>
          {latest ? `ALIGNMENT R${latest.revision}` : "NOT ALIGNED"}
        </Badge>
      </div>
      <div className="quality-list">
        {session.sensors.map((s) => (
          <div key={s.id}>
            <b>{s.name}</b>
            <Badge tone={s.status === "ready" ? "teal" : "amber"}>
              {s.status}
            </Badge>
            <span>
              {s.samples.toLocaleString()} samples ·{" "}
              {(s.duration_us / 1e6).toFixed(2)} s
            </span>
            <details>
              <summary>Actual quality report</summary>
              <pre>{JSON.stringify(s.quality, null, 2)}</pre>
            </details>
          </div>
        ))}
        {session.videos.map((v) => (
          <div key={v.id}>
            <b>{v.name}</b>
            <Badge tone={v.status === "ready" ? "teal" : "amber"}>
              {v.status}
            </Badge>
            <span>
              {v.width} × {v.height} · {(v.duration_us / 1e6).toFixed(2)} s
            </span>
          </div>
        ))}
        {session.jobs
          .filter(
            (j) =>
              j.state === "failed" &&
              ["normalize", "video_probe"].includes(j.kind),
          )
          .map((j) => (
            <p className="error-box" key={j.id}>
              {j.kind}: {j.error}
            </p>
          ))}
        {!session.sensors.length && !session.videos.length && (
          <p>No observations yet. Capture above or upload a recording.</p>
        )}
      </div>
      {sensors.length > 0 && videos.length > 0 && (
        <form className="collection-form" onSubmit={save}>
          <label>
            Sensor source
            <select
              value={sensor}
              onChange={(e) => setSensorId(e.target.value)}
            >
              {sensors.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Video source
            <select value={video} onChange={(e) => setVideoId(e.target.value)}>
              {videos.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Start cue · sensor seconds
            <input
              type="number"
              min="0"
              max="1200"
              step="0.001"
              required
              value={startSensor}
              onChange={(e) => setStartSensor(e.target.value)}
            />
          </label>
          <label>
            Start cue · video seconds
            <input
              type="number"
              min="0"
              max="600"
              step="0.001"
              required
              value={startVideo}
              onChange={(e) => setStartVideo(e.target.value)}
            />
          </label>
          <label>
            End cue · sensor seconds (optional)
            <input
              type="number"
              min="0"
              max="1200"
              step="0.001"
              value={endSensor}
              onChange={(e) => setEndSensor(e.target.value)}
            />
          </label>
          <label>
            End cue · video seconds (optional)
            <input
              type="number"
              min="0"
              max="600"
              step="0.001"
              required={endSensor !== ""}
              value={endVideo}
              onChange={(e) => setEndVideo(e.target.value)}
            />
          </label>
          <label>
            Cue timing uncertainty · seconds
            <input
              type="number"
              min="0"
              max="2"
              step="0.001"
              required
              value={uncertainty}
              onChange={(e) => setUncertainty(e.target.value)}
            />
          </label>
          <label>
            Pairing / timing evidence
            <input
              maxLength={1500}
              required
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Same attempt; visible start/end cue; approximate localization"
            />
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={paired}
              onChange={(e) => setPaired(e.target.checked)}
            />
            I attest that these sources record the same attempt.
          </label>
          <p>
            Sensor + offset = video/session time. Proposed offset:{" "}
            {offset.toFixed(3)} s.{" "}
            {endResidual !== null &&
              `End residual: ${endResidual.toFixed(3)} s.`}{" "}
            This is offset-only alignment; drift is not corrected.
          </p>
          <button className="button primary" disabled={busy}>
            Save alignment revision
          </button>
          <ErrorBox error={error} />
        </form>
      )}
      {latest && (
        <p>
          Saved offset {(latest.offset_us / 1e6).toFixed(3)} s · revision{" "}
          {latest.revision}. Evidence:{" "}
          {String(latest.evidence.note || "No cue evidence recorded")}.{" "}
          {latest.evidence.end_residual_us !== undefined &&
            `End residual ${Number(latest.evidence.end_residual_us) / 1e6} s.`}
        </p>
      )}
      <div className="capture-actions">
        <Link className="button primary" href={`/sessions/${session.id}`}>
          Inspect synchronized replay <ArrowRight size={15} />
        </Link>
        <Link className="button" href={`/sessions/${session.id}?tab=research`}>
          Open Sensor Fusion Challenge
        </Link>
      </div>
    </section>
  );
}
