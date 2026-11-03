"""Optional external smoke-test footage. Not redistributed; not a tennis validation dataset."""
import hashlib
import urllib.request
import subprocess
import os
from pathlib import Path

url = "https://mediapipe.dev/images/mobile/pose_world_landmarks.mp4"
target = Path(__file__).resolve().parents[1] / "data/private/pose-upstream.mp4"
target.parent.mkdir(parents=True, exist_ok=True)
with urllib.request.urlopen(url, timeout=30) as response:
    content = response.read(30_000_001)
if len(content) > 30_000_000:
    raise RuntimeError("Verification video exceeds expected size limit")
target.write_bytes(content)
print(f"Official MediaPipe documentation clip: {len(content)} bytes; SHA-256 {hashlib.sha256(content).hexdigest()}")
print("Source:", url)
# The upstream clip has invalid random-access H.264 references in Chromium.
# Preserve it and generate a clearly identified, seekable software-test derivative.
subprocess.run(["docker","run","--rm","--network","none",
                *(["--user",f"{os.getuid()}:{os.getgid()}"] if hasattr(os,"getuid") else []),
                "-v",f"{target.parent.resolve()}:/verify",
                "--entrypoint","ffmpeg","rallysense-api:local","-v","error","-y","-i","/verify/pose-upstream.mp4",
                "-an","-c:v","libx264","-crf","18","-g","25","-keyint_min","25","-sc_threshold","0",
                "-pix_fmt","yuv420p","-movflags","+faststart","/verify/pose-sample.mp4"],check=True)
derived=target.with_name("pose-sample.mp4").read_bytes()
print("Seekable test derivative SHA-256:",hashlib.sha256(derived).hexdigest())
