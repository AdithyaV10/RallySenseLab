import type { PoseLandmarker } from "@mediapipe/tasks-vision";
import { api, Pose, PoseFrame } from "@/lib/api";

type WorkerResult = {
  id: number;
  type: string;
  message?: string;
  landmarks: PoseFrame["landmarks"];
  world_landmarks: PoseFrame["world_landmarks"];
};
export async function extractPose(
  videoId: string,
  onProgress: (message: string) => void,
  signal: AbortSignal,
): Promise<Pose> {
  const info = await fetch("/model-info.json").then((r) => {
    if (!r.ok) throw new Error("Run the asset setup script first");
    return r.json();
  });
  let worker: Worker | null = null,
    fallback: PoseLandmarker | null = null,
    requestId = 0;
  let track: Pose | null = null;
  const video = document.createElement("video");
  video.muted = true;
  video.playsInline = true;
  video.preload = "auto";
  video.style.cssText =
    "position:fixed;width:2px;height:2px;opacity:0;pointer-events:none;bottom:0";
  document.body.appendChild(video);
  function call(
    type: string,
    extra: Record<string, unknown> = {},
    transfer: Transferable[] = [],
  ): Promise<WorkerResult> {
    const id = ++requestId;
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        cleanup();
        reject(new Error("Pose worker timed out"));
      }, 60000);
      const listener = (e: MessageEvent<WorkerResult>) => {
        if (e.data.id !== id) return;
        cleanup();
        if (e.data.type === "error") reject(new Error(e.data.message));
        else resolve(e.data);
      };
      const failure = () => {
        cleanup();
        reject(new Error("Browser could not initialize the pose worker"));
      };
      function cleanup() {
        clearTimeout(timeout);
        worker?.removeEventListener("message", listener);
        worker?.removeEventListener("error", failure);
      }
      worker!.addEventListener("message", listener);
      worker!.addEventListener("error", failure);
      worker!.postMessage({ id, type, ...extra }, transfer);
    });
  }
  try {
    if (!("requestVideoFrameCallback" in HTMLVideoElement.prototype))
      throw new Error(
        "This browser lacks frame presentation callbacks. Use current Chrome, Edge, Firefox, or Safari.",
      );
    onProgress("Initializing MediaPipe CPU runtime…");
    let executor: "worker" | "main_thread_fallback" = "worker";
    try {
      worker = new Worker("/pose-worker.js");
      await call("init");
    } catch (error) {
      worker?.terminate();
      worker = null;
      executor = "main_thread_fallback";
      onProgress(
        `Worker unavailable (${error instanceof Error ? error.message : "unsupported"}). Using the main-thread CPU fallback…`,
      );
      const { FilesetResolver, PoseLandmarker } =
        await import("@mediapipe/tasks-vision");
      fallback = await PoseLandmarker.createFromOptions(
        await FilesetResolver.forVisionTasks("/vendor/wasm"),
        {
          baseOptions: {
            modelAssetPath: "/vendor/pose_landmarker_lite.task",
            delegate: "CPU",
          },
          runningMode: "VIDEO",
          numPoses: 1,
        },
      );
    }
    track = await api<Pose>(`/videos/${videoId}/pose-tracks`, {
      method: "POST",
      body: JSON.stringify({ ...info, executor }),
    });
    const frames: PoseFrame[] = [];
    let nextSample = 0,
      processing: Promise<void> = Promise.resolve(),
      batchIndex = 0,
      buffer: PoseFrame[] = [];
    async function flush() {
      if (!buffer.length) return;
      const payload = buffer;
      buffer = [];
      await api(`/pose-tracks/${track!.id}/batches/${batchIndex++}`, {
        method: "PUT",
        body: JSON.stringify({ frames: payload }),
      });
    }
    await new Promise<void>((resolve, reject) => {
      const abort = () => {
        video.pause();
        reject(new Error("Pose extraction cancelled"));
      };
      signal.addEventListener("abort", abort, { once: true });
      video.onerror = () => {
        signal.removeEventListener("abort", abort);
        reject(
          new Error("Browser cannot decode this video. Use MP4 H.264 or WebM."),
        );
      };
      video.onended = () => {
        signal.removeEventListener("abort", abort);
        processing.then(resolve, reject);
      };
      const callback: VideoFrameRequestCallback = (_now, meta) => {
        if (signal.aborted) return;
        if (meta.mediaTime >= nextSample) {
          const timeUs = Math.round(meta.mediaTime * 1e6);
          nextSample = meta.mediaTime + 0.095;
          processing = (async () => {
            let result: Pick<PoseFrame, "landmarks" | "world_landmarks">;
            if (worker) {
              const bitmap = await createImageBitmap(video);
              result = await call(
                "frame",
                { bitmap, timestampMs: timeUs / 1000 },
                [bitmap],
              );
            } else {
              const r = fallback!.detectForVideo(video, timeUs / 1000);
              result = {
                landmarks: r.landmarks[0] || [],
                world_landmarks: r.worldLandmarks[0] || [],
              };
            }
            const frame = {
              t_video_us: timeUs,
              landmarks: result.landmarks,
              world_landmarks: result.world_landmarks,
            };
            frames.push(frame);
            buffer.push(frame);
            onProgress(
              `${executor === "worker" ? "Worker" : "Main-thread fallback"} · ${frames.length} frames · ${meta.mediaTime.toFixed(1)} / ${video.duration.toFixed(1)} s`,
            );
            if (buffer.length >= 100) await flush();
          })();
          processing.then(() => {
            if (!video.ended && !signal.aborted)
              video.requestVideoFrameCallback(callback);
          }, reject);
        } else video.requestVideoFrameCallback(callback);
      };
      video.onloadeddata = () => {
        video.requestVideoFrameCallback(callback);
        video.play().catch(reject);
      };
      video.src = `/api/v1/videos/${videoId}/content`;
      video.load();
    });
    if (signal.aborted) throw new Error("Pose extraction cancelled");
    await flush();
    const result = await api<Pose>(`/pose-tracks/${track.id}/complete`, {
      method: "POST",
    });
    onProgress(`Complete · ${frames.length} sampled frames · ${executor}`);
    return result;
  } catch (error) {
    if (track)
      await api(`/pose-tracks/${track.id}/fail`, { method: "POST" }).catch(
        () => {},
      );
    throw error;
  } finally {
    video.pause();
    video.removeAttribute("src");
    video.load();
    video.remove();
    worker?.terminate();
    fallback?.close();
  }
}
