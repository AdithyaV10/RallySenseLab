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
  targetHz: 10 | 30 = 10,
  samplingMethod: "playback" | "seek_backpressure" = "playback",
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
  video.playbackRate = targetHz === 30 ? 0.5 : 1;
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
      body: JSON.stringify({
        ...info,
        executor,
        sample_target_hz: targetHz,
        playback_rate: video.playbackRate,
        sampling_method: samplingMethod,
      }),
    });
    // Keep only the bounded staging batch, rather than retaining an entire track in RAM.
    let frameCount = 0,
      lastTimeUs = -1;
    let nextSample = 0,
      processing: Promise<void> = Promise.resolve(),
      batchIndex = 0,
      bufferBytes = 12,
      buffer: PoseFrame[] = [];
    async function flush() {
      if (!buffer.length) return;
      if (batchIndex >= 200)
        throw new Error("Pose batch capacity reached (200)");
      const payload = buffer;
      buffer = [];
      bufferBytes = 12;
      await api(`/pose-tracks/${track!.id}/batches/${batchIndex++}`, {
        method: "PUT",
        body: JSON.stringify({ frames: payload }),
      });
    }
    async function observe(timeUs: number) {
      if (signal.aborted) throw new Error("Pose extraction cancelled");
      if (timeUs <= lastTimeUs) return;
      if (frameCount >= 30_000)
        throw new Error("Pose observation capacity reached (30,000)");
      let result: Pick<PoseFrame, "landmarks" | "world_landmarks">;
      if (worker) {
        const bitmap = await createImageBitmap(video);
        result = await call("frame", { bitmap, timestampMs: timeUs / 1000 }, [
          bitmap,
        ]);
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
      frameCount++;
      lastTimeUs = timeUs;
      const bytes = JSON.stringify(frame).length + 1;
      if (bufferBytes + bytes > 1_900_000) await flush();
      buffer.push(frame);
      bufferBytes += bytes;
      onProgress(
        `${samplingMethod} · ${executor} · ${frameCount} frames · ${(timeUs / 1e6).toFixed(2)} / ${video.duration.toFixed(2)} s`,
      );
      if (buffer.length >= 200) await flush();
    }
    if (samplingMethod === "seek_backpressure") {
      await new Promise<void>((resolve, reject) => {
        const timer = setTimeout(
          () => reject(new Error("Video loading timed out")),
          20000,
        );
        video.onloadeddata = () => {
          clearTimeout(timer);
          resolve();
        };
        video.onerror = () => {
          clearTimeout(timer);
          reject(new Error("Browser cannot decode this video"));
        };
        video.src = `/api/v1/videos/${videoId}/content`;
        video.load();
      });
      video.pause();
      for (
        let target = 0;
        target < video.duration - 0.001;
        target += 1 / targetHz
      ) {
        if (signal.aborted) throw new Error("Pose extraction cancelled");
        if (document.hidden)
          throw new Error(
            "Keep the extraction tab visible; hidden pages cannot guarantee frame callbacks",
          );
        const timeUs = await new Promise<number>((resolve, reject) => {
          let callback = 0;
          const cleanup = () => {
            clearTimeout(timer);
            signal.removeEventListener("abort", abort);
            if (callback) video.cancelVideoFrameCallback(callback);
          };
          const abort = () => {
            cleanup();
            reject(new Error("Pose extraction cancelled"));
          };
          const timer = setTimeout(() => {
            cleanup();
            reject(
              new Error(
                "Seek frame callback timed out. Retry using playback sampling in this browser.",
              ),
            );
          }, 15000);
          signal.addEventListener("abort", abort, { once: true });
          callback = video.requestVideoFrameCallback((_now, meta) => {
            cleanup();
            resolve(Math.round(meta.mediaTime * 1e6));
          });
          video.currentTime = Math.max(0.001, target);
        });
        // Use the presented frame timestamp, never the requested seek target.
        await observe(timeUs);
      }
    } else
      await new Promise<void>((resolve, reject) => {
        const abort = () => {
          video.pause();
          reject(new Error("Pose extraction cancelled"));
        };
        signal.addEventListener("abort", abort, { once: true });
        video.onerror = () => {
          signal.removeEventListener("abort", abort);
          reject(
            new Error(
              "Browser cannot decode this video. Use MP4 H.264 or WebM.",
            ),
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
            nextSample = meta.mediaTime + 0.95 / targetHz;
            processing = observe(timeUs);
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
      body: JSON.stringify({ expected_frames: frameCount }),
    });
    onProgress(`Complete · ${frameCount} sampled frames · ${executor}`);
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
