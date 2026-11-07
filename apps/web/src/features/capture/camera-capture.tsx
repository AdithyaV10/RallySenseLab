"use client";
import { useEffect, useRef, useState } from "react";
import { Camera, Download } from "lucide-react";
import { api, type SessionDetail } from "@/lib/api";
import { Badge, ErrorBox } from "@/components/ui";
import { downloadBlob } from "./motion";

export function CameraCapture({
  session,
  refresh,
}: {
  session: SessionDetail;
  refresh: () => void;
}) {
  const [provenance, setProvenance] = useState<"recorded" | "synthetic">(
    "recorded",
  );
  const video = useRef<HTMLVideoElement>(null),
    stream = useRef<MediaStream | null>(null),
    recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]),
    bytes = useRef(0),
    started = useRef(""),
    startClock = useRef(0),
    stopReason = useRef("operator");
  const unsaved = useRef(false);
  const [recording, setRecording] = useState(false),
    [clip, setClip] = useState<Blob | null>(null),
    [duration, setDuration] = useState(0),
    [error, setError] = useState<unknown>(null),
    [busy, setBusy] = useState(false),
    [reason, setReason] = useState("operator");
  function stop(reason = "operator") {
    stopReason.current = reason;
    if (recorder.current?.state === "recording") recorder.current.stop();
    stream.current?.getTracks().forEach((t) => t.stop());
  }
  useEffect(() => {
    const hidden = () => {
      if (document.hidden) stop("Page hidden / screen locked");
    };
    const guard = (event: BeforeUnloadEvent) => {
      if (unsaved.current) event.preventDefault();
    };
    window.addEventListener("beforeunload", guard);
    document.addEventListener("visibilitychange", hidden);
    return () => {
      document.removeEventListener("visibilitychange", hidden);
      window.removeEventListener("beforeunload", guard);
      stop("Component closed");
    };
  }, []);
  useEffect(() => {
    if (!recording) return;
    const timer = setInterval(() => {
      const elapsed = (performance.now() - startClock.current) / 1000;
      setDuration(elapsed);
      if (elapsed >= 600) stop("10 minute limit");
    }, 250);
    return () => clearInterval(timer);
  }, [recording]);
  async function start() {
    setError(null);
    try {
      if (
        !window.isSecureContext ||
        !navigator.mediaDevices?.getUserMedia ||
        typeof MediaRecorder === "undefined"
      )
        throw new Error(
          "Camera recording requires a supported browser in HTTPS or localhost. Record with your camera app and upload the file below.",
        );
      if (
        clip &&
        !window.confirm(
          "Replace the captured clip? Save or export it first to retain it.",
        )
      )
        return;
      const media = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: "environment" },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      stream.current = media;
      if (video.current) {
        video.current.srcObject = media;
        await video.current.play();
      }
      const mimeType = [
        "video/webm;codecs=vp8",
        "video/mp4",
        "video/webm",
      ].find((t) => MediaRecorder.isTypeSupported(t));
      const rec = new MediaRecorder(
        media,
        mimeType ? { mimeType, videoBitsPerSecond: 2_500_000 } : undefined,
      );
      recorder.current = rec;
      chunks.current = [];
      bytes.current = 0;
      setClip(null);
      setDuration(0);
      rec.ondataavailable = (e) => {
        if (e.data.size) {
          chunks.current.push(e.data);
          bytes.current += e.data.size;
          if (bytes.current >= 100 * 1024 * 1024) stop("100 MiB memory limit");
        }
      };
      rec.onstop = () => {
        unsaved.current = true;
        setClip(new Blob(chunks.current, { type: rec.mimeType }));
        setReason(stopReason.current);
        setRecording(false);
        media.getTracks().forEach((t) => t.stop());
      };
      rec.onerror = () => {
        setError(
          new Error(
            "Camera recording interrupted. Any completed chunks remain exportable; validate the result before use.",
          ),
        );
        stop("MediaRecorder error");
      };
      started.current = new Date().toISOString();
      startClock.current = performance.now();
      rec.start(1000);
      unsaved.current = true;
      setRecording(true);
    } catch (e) {
      stream.current?.getTracks().forEach((t) => t.stop());
      setError(e);
    }
  }
  async function save() {
    if (!clip) return;
    setBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.set(
        "file",
        new File(
          [clip],
          `camera.${clip.type.includes("mp4") ? "mp4" : "webm"}`,
          { type: clip.type },
        ),
      );
      form.set(
        "metadata",
        JSON.stringify({
          provenance,
          capture: {
            source: "browser_camera",
            started_at_utc: started.current,
            timestamp_basis:
              "MediaRecorder encoded video timeline; UTC start is descriptive, not sensor synchronization",
            browser: navigator.userAgent.slice(0, 400),
            device_model: String(
              session.collection_profile.device_model ?? "unknown",
            ),
            stop_reason: stopReason.current,
          },
        }),
      );
      await api(`/sessions/${session.id}/videos`, {
        method: "POST",
        body: form,
      });
      unsaved.current = false;
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
        <Camera size={20} />
        <h2>Camera recording</h2>
        <Badge>{recording ? "RECORDING" : "OPTIONAL · NO AUDIO"}</Badge>
      </div>
      <p>
        Record the visible movement with a fixed camera. Camera and sensor
        clocks must still be aligned using observable cues.
      </p>
      <label>
        Camera source provenance
        <select
          aria-label="Camera source provenance"
          value={provenance}
          disabled={recording || !!clip}
          onChange={(e) => setProvenance(e.target.value as typeof provenance)}
        >
          <option value="recorded">Recorded camera observations</option>
          <option value="synthetic">Synthetic software camera test</option>
        </select>
      </label>
      <video
        ref={video}
        muted
        playsInline
        className="capture-preview"
        aria-label="Camera preview"
      />
      <p role="status">
        {duration.toFixed(1)} s{" "}
        {clip
          ? `· ${(clip.size / 1024 / 1024).toFixed(2)} MiB captured · ${reason}`
          : recording
            ? "· Keep this page visible"
            : "· Camera access requested only when recording starts"}
      </p>
      <div className="capture-actions">
        {recording ? (
          <button className="button danger" onClick={() => stop()}>
            Stop camera
          </button>
        ) : (
          <button className="button" onClick={start}>
            <Camera size={15} />
            Start camera recording
          </button>
        )}
        <button
          className="button"
          disabled={!clip || recording}
          onClick={() =>
            clip &&
            downloadBlob(
              clip,
              `camera.${clip.type.includes("mp4") ? "mp4" : "webm"}`,
            )
          }
        >
          <Download size={15} />
          Export clip
        </button>
        <button
          className="button"
          disabled={!clip || recording || busy}
          onClick={save}
        >
          {busy ? "Saving…" : "Save video to session"}
        </button>
      </div>
      <ErrorBox error={error} />
      <p className="fine-print">
        Up to 10 minutes / approximately 100 MiB in memory. Save or export
        before navigating. Browser codec and seekability vary; the actual
        uploaded file is probed by the worker. External camera files remain
        supported.
      </p>
    </section>
  );
}
