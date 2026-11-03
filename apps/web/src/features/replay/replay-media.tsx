"use client";
import { useEffect, useRef, useState } from "react";
import { Maximize, ScanLine, VideoOff } from "lucide-react";
import { PoseFrame, Video } from "@/lib/api";
import { nearestFrame, containRect } from "@/lib/timeline";
import { Badge } from "@/components/ui";
import { Court } from "@/components/court";
const connections = [
  [11, 12],
  [11, 13],
  [13, 15],
  [12, 14],
  [14, 16],
  [11, 23],
  [12, 24],
  [23, 24],
  [23, 25],
  [25, 27],
  [24, 26],
  [26, 28],
  [27, 29],
  [29, 31],
  [28, 30],
  [30, 32],
];
export function ReplayMedia({
  video,
  frames,
  timeUs,
  playing,
  rate,
  onTime,
  onEnded,
  synthetic,
  seekToken,
}: {
  video?: Video;
  frames: PoseFrame[];
  timeUs: number;
  playing: boolean;
  rate: number;
  onTime: (time: number) => void;
  onEnded: () => void;
  synthetic: boolean;
  seekToken: number;
}) {
  const element = useRef<HTMLVideoElement>(null),
    container = useRef<HTMLDivElement>(null);
  const stage = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 640, height: 360 });
  const [sourceSize, setSourceSize] = useState<{
    width: number;
    height: number;
  } | null>(null);
  useEffect(() => {
    const node = stage.current;
    if (!node) return;
    const observer = new ResizeObserver(([entry]) =>
      setDimensions({
        width: entry.contentRect.width,
        height: entry.contentRect.height,
      }),
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);
  const [overlay, setOverlay] = useState(true),
    [error, setError] = useState("");
  const clock = useRef(onTime);
  useEffect(() => {
    clock.current = onTime;
  }, [onTime]);
  useEffect(() => {
    const v = element.current;
    if (!v) return;
    let id = 0,
      lastUpdate = 0;
    const update: VideoFrameRequestCallback = (_n, meta) => {
      if (_n - lastUpdate >= 50 || !playing) {
        clock.current(Math.round(meta.mediaTime * 1e6));
        lastUpdate = _n;
      }
      id = v.requestVideoFrameCallback(update);
    };
    if (v.requestVideoFrameCallback) id = v.requestVideoFrameCallback(update);
    return () => {
      if (id) v.cancelVideoFrameCallback(id);
    };
  }, [video?.id, playing]);
  useEffect(() => {
    const v = element.current;
    if (!v) return;
    v.playbackRate = rate;
    if (playing) v.play().catch((e) => setError(String(e)));
    else v.pause();
  }, [playing, rate, video?.id]);
  // Only explicit seeks change video.currentTime. Frame updates never seek the video back.
  useEffect(() => {
    const v = element.current;
    if (v && Math.abs(v.currentTime - timeUs / 1e6) > 0.02)
      v.currentTime =
        timeUs /
        1e6; /* timeUs is intentionally sampled only at a seek intent */
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seekToken, video?.id]);
  const frame = error ? null : nearestFrame(frames, timeUs);
  return (
    <div className="viewer-panel" ref={container}>
      <div className="panel-heading">
        <div className="panel-title">
          <span className="status-light" />
          <h3>
            {video
              ? "Video observation"
              : synthetic
                ? "Motion illustration"
                : "Video observation"}
          </h3>
        </div>
        <div className="viewer-tools">
          {frames.length > 0 && (
            <button
              className={`icon-button ${overlay ? "selected" : ""}`}
              aria-label="Toggle pose overlay"
              aria-pressed={overlay}
              onClick={() => setOverlay(!overlay)}
            >
              <ScanLine size={15} />
            </button>
          )}
          <button
            className="icon-button"
            aria-label="Fullscreen viewer"
            onClick={() => container.current?.requestFullscreen()}
          >
            <Maximize size={14} />
          </button>
        </div>
      </div>
      <div className="media-stage" ref={stage}>
        {video ? (
          <div
            className="video-fit"
            style={containRect(
              sourceSize?.width || video.width,
              sourceSize?.height || video.height,
              dimensions.width,
              dimensions.height,
            )}
          >
            <video
              key={video.id}
              ref={element}
              src={`/api/v1/videos/${video.id}/content`}
              playsInline
              onLoadedMetadata={(e) =>
                setSourceSize({
                  width: e.currentTarget.videoWidth,
                  height: e.currentTarget.videoHeight,
                })
              }
              onEnded={onEnded}
              onLoadedData={() => setError("")}
              onPlaying={() => setError("")}
              onError={() => {
                onEnded();
                setError(
                  "Video decoding failed. Use a seekable H.264 re-encode or a compatible browser.",
                );
              }}
              onSeeked={(e) =>
                onTime(Math.round(e.currentTarget.currentTime * 1e6))
              }
            />
            {overlay && frame && frame.landmarks.length === 33 && (
              <svg
                className="pose-overlay"
                viewBox="0 0 1000 1000"
                preserveAspectRatio="none"
                aria-label="MediaPipe pose overlay"
              >
                <g stroke="#56e1b9" strokeWidth="3" fill="none">
                  {connections.map(([a, b]) => {
                    const x = frame.landmarks[a],
                      y = frame.landmarks[b];
                    return (x.visibility ?? 0) > 0.5 &&
                      (y.visibility ?? 0) > 0.5 ? (
                      <line
                        key={`${a}-${b}`}
                        x1={x.x * 1000}
                        y1={x.y * 1000}
                        x2={y.x * 1000}
                        y2={y.y * 1000}
                      />
                    ) : null;
                  })}
                </g>
                {frame.landmarks.map((p, i) =>
                  (p.visibility ?? 0) > 0.5 ? (
                    <circle
                      key={i}
                      cx={p.x * 1000}
                      cy={p.y * 1000}
                      r="4"
                      fill="#f5c47e"
                    />
                  ) : null,
                )}
              </svg>
            )}
          </div>
        ) : synthetic ? (
          <Court time={timeUs / 1e6} />
        ) : (
          <div className="no-video">
            <VideoOff size={31} />
            <h3>Signal-only observation</h3>
            <p>
              Add video in Data & processing to enable synchronized video and
              pose.
            </p>
          </div>
        )}
        <div className="viewer-badges">
          <Badge tone={synthetic && !video ? "amber" : "neutral"}>
            {synthetic && !video
              ? "Programmatic animation"
              : video
                ? `${video.width} × ${video.height}`
                : "No video"}
          </Badge>
          {frame && (
            <Badge tone="teal">
              {frame.landmarks.length ? "POSE OBSERVED" : "NO PERSON DETECTED"}
            </Badge>
          )}
        </div>
        {error && (
          <div className="error-box" role="alert">
            {error}
          </div>
        )}
      </div>
      <div className="viewer-bottom">
        <span>
          {video
            ? video.name
            : synthetic
              ? "Illustrated fixture playback · not extracted pose"
              : "Waiting for a recording"}
        </span>
        <span>{video ? "SOURCE / VIDEO" : "SOURCE / GENERATED"}</span>
      </div>
      {frame?.features && (
        <div className="pose-feature-strip">
          <span>IMAGE-SPACE FEATURES</span>
          <span>
            Elbow {frame.features.elbow_angle_deg_2d?.toFixed(1) ?? "—"}°
          </span>
          <span>
            Wrist {frame.features.wrist_speed_torso_units_s?.toFixed(2) ?? "—"}{" "}
            torso units/s
          </span>
        </div>
      )}
    </div>
  );
}
