/* global importScripts, Vision */
// Classic worker is intentional: the installed MediaPipe WASM loader uses importScripts.
importScripts("/vendor/vision_bundle.js");
let landmarker;
self.onmessage = async ({ data }) => {
  try {
    if (data.type === "init") {
      const files = await Vision.FilesetResolver.forVisionTasks(
        `${self.location.origin}/vendor/wasm`,
      );
      landmarker = await Vision.PoseLandmarker.createFromOptions(files, {
        baseOptions: {
          modelAssetPath: `${self.location.origin}/vendor/pose_landmarker_lite.task`,
          delegate: "CPU",
        },
        runningMode: "VIDEO",
        numPoses: 1,
        outputSegmentationMasks: false,
      });
      self.postMessage({ id: data.id, type: "ready" });
    } else if (data.type === "frame") {
      try {
        const result = landmarker.detectForVideo(data.bitmap, data.timestampMs);
        self.postMessage({
          id: data.id,
          type: "result",
          landmarks: result.landmarks[0] || [],
          world_landmarks: result.worldLandmarks[0] || [],
        });
      } finally {
        data.bitmap.close();
      }
    }
  } catch (error) {
    self.postMessage({
      id: data.id,
      type: "error",
      message: error instanceof Error ? error.message : String(error),
    });
  }
};
