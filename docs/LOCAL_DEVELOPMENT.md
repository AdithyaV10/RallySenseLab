# Local startup and demonstration

The recommended runtime uses Docker Desktop with Linux containers. Ports 3000, 8000, and 5433 must be free. Services publish only on `127.0.0.1`. The first build needs registry access and the checksum-verified official MediaPipe model download. It does not need a cloud account or physical sensor.

## Complete application

From Windows PowerShell:

```powershell
Set-Location C:\RallySenseLab
docker compose up -d --build
docker compose ps
```

Open `http://127.0.0.1:3000`. API docs: `http://127.0.0.1:8000/docs`. PostgreSQL is available locally on port 5433 for developer tools; the application uses the internal Docker service name.

The API startup runs `alembic upgrade head` before serving requests. The worker waits for API readiness. The web image builds Next.js standalone output and locally hosts the pinned model/WASM. `.env.example` documents local settings; default credentials are development-only. Configure `.env` before the first database initialization if you want different credentials. Changing the database password environment variable after volume initialization does not change an existing PostgreSQL role password.

For an explicit migration command:

```powershell
docker compose run --rm api alembic upgrade head
```

Stop services while preserving recordings/database volumes:

```powershell
docker compose stop
```

`docker compose down` also preserves named volumes unless `-v` is requested. Do not remove volumes to troubleshoot ordinary startup failures. No public deployment or remote hosting is configured.

## Demonstration walkthrough

1. Select **Explore the demo** from the landing page or **Open demonstration** from the library. Repeated selection opens the same synthetic session.
2. Wait for actual normalization/inference jobs. The fixture contains 1,801 rows at 100 Hz over 18 seconds. Five calculated gyro peaks and five generated reference markers should appear. This is software verification, not measured tennis accuracy.
3. Click an event, click a plot, drag the timeline, change speed, and play/pause. The programmatic animation, signal cursor, and shared time update together. The animation is explicitly labeled and is not extracted pose.
4. Add a manual reference at the cursor. Edit its timestamp or delete it. Generated fixture references cannot be edited as if they were human labels.
5. Save a nonzero sensor offset. Positive moves sensor events later relative to video/session time. The old run keeps its original alignment and shows a stale-alignment notice. Run the baseline to create results for the new revision.
6. Enable **Blinded labels** to hide sensor charts, event counts/markers and prediction navigation while annotating video.
7. In **Data & processing**, inspect real jobs or upload your own sources. A gyro-only recording works with explicit column mapping; an accelerometer-only recording can be viewed but cannot run the gyro detector.
8. For a real video, upload a supported file, wait for validation, return to replay and select **Extract pose**. Keep the tab open. The UI reports actual sampled frames/media position. After completion, inspect skeleton overlay, detection coverage and image-space features. Retry creates a new track.

## Step 3 research walkthrough

Open any session and choose **Sensor Fusion Challenge**. Choose **Open paired synthetic lab** for a hardware-free path through all three modes. This creates a separate generated stick-figure/landmark/IMU fixture; it is visibly labeled synthetic and its landmarks are not MediaPipe output. Freeze its generated reference set, choose that snapshot, then run IMU, video and multimodal association. Compare actual results and try a deliberate synchronization error. See [EXPERIMENTS.md](EXPERIMENTS.md) for the full guide and a practical paired-recording collection protocol.

For actual video, extraction now offers a 10 Hz target and a 30 Hz target with half-speed processing playback. Inspect achieved cadence and gaps in the quality report. Keep the tab visible; neither target guarantees exhaustive decoding. The existing verified worker and initialization-failure fallback remain available.

Optional reproducible local research smoke check (host Python/uv dependencies installed):

```powershell
uv run --project apps/api python scripts/verify-research.py
```

This runs the real algorithms for clean and corrupted synthetic conditions, preserves original observations, and writes `docs/evidence/step3-local-verification.json`. It establishes software behavior only. Full container/browser/test commands and actual outcomes are recorded in [TESTING.md](TESTING.md).

## Native frontend with container API/database/worker

Node 24 and npm are required for this workflow. PowerShell's npm.ps1 is blocked in the inspected environment; use `npm.cmd`.

```powershell
docker compose -f docker-compose.yml -f infrastructure/compose.dev.yml up -d --build db api worker
npm.cmd ci --prefix apps/web
node scripts/fetch-assets.mjs
npm.cmd --prefix apps/web run dev
```

The override mounts API sources/tests/migrations read-only. Restart API/worker after Python edits; they do not auto-reload. Avoid starting the Docker web service simultaneously with the native server on port 3000.

Python development uses `uv sync --project apps/api --frozen`. Native API startup needs FFprobe on PATH for video validation; the API container supplies the verified FFmpeg/FFprobe installation and is the supported default. For an optional native API terminal:

```powershell
Set-Location C:\RallySenseLab\apps\api
uv run alembic upgrade head
uv run uvicorn rallysense.main:app --host 127.0.0.1 --port 8000
```

Use a separate terminal for `uv run python -m rallysense.worker` and stop the corresponding container services first. Native storage defaults relative to the current working directory; use an absolute `STORAGE_ROOT` consistently if mixing native processes. Native and container artifact roots are not interchangeable.

## Troubleshooting

- **Docker engine unavailable:** start Docker Desktop in Linux-container mode and check `docker info`. The earlier Step 1 engine failure was absent at Step 2; actual PostgreSQL/API startup was verified.
- **Port in use:** stop only the owned application process/container using that port; do not terminate unrelated Node or PostgreSQL processes.
- **API unavailable:** inspect `docker compose ps` and `docker compose logs api worker`. Wait for migrations/health readiness, not a fake progress bar.
- **Invalid CSV:** inspect the failed job, correct exact column names/units and import again. Decimal-point numeric text is supported; ambiguous locale formats and decreasing/duplicate times are rejected. ZIP imports are not supported; extract phyphox CSVs first.
- **Unsupported video:** use MP4 H.264 or WebM VP8/VP9, <=500 MiB, <=10 min, <=1920×1080 pixels. Both FFprobe validation and the active browser must support decoding. The MVP does not automatically transcode.
- **Pose worker failure:** initialization uses the documented main-thread CPU fallback and records it. A failure mid-track marks extraction failed. Background-tab throttling can reduce sampled coverage. Keep the page visible for best results.
- **Failed cleanup/job:** inspect its safe error via the API and local worker logs. System readiness can retry failed source normalization/video probing as a new validation job. Rerun scientific experiments as new runs. Cleanup and other job failures still require log investigation; preserve volumes rather than deleting storage manually.

## Opt-in trusted HTTPS for phone capture

The ordinary Compose application stays on loopback. A phone's `127.0.0.1` refers to the phone, not the workstation. Browser motion/camera APIs need a secure context; an untrusted certificate warning is not equivalent to a trusted HTTPS origin. Physical iOS/Android verification remains required.

For a private, trusted LAN only:

1. Install locked native web dependencies (`npm.cmd ci --prefix apps/web`) and keep the Docker API/database/worker running. Use your workstation's actual RFC1918 IPv4 address shown by `Get-NetIPAddress -AddressFamily IPv4`. Use a private trusted network, not public Wi-Fi.
2. Independently install/review mkcert if desired, generate a certificate whose SAN includes that exact IP, and install only its public root CA certificate into the phone's trust store using the operating system's documented process. [mkcert's official mobile instructions](https://github.com/FiloSottile/mkcert) explain that mobile trust is a separate step. Do not share `rootCA-key.pem` or private keys. Certificate/key files belong in ignored `certificates/`. This agent has not installed a CA or changed trust settings.
3. Set a unique `SITE_ACCESS_PASSWORD` of at least 20 characters and set `LOCAL_TOKEN` to match your running API in the same PowerShell process. Do not put either in URLs, browser code or Git. The browser username is `lab`; its workspace password differs from the internal API token.
4. Prepare the exact configuration first. The command below validates paths/IP/password and opens no listener:

```powershell
.\scripts\start-phone-https.ps1 -LanAddress 192.168.1.50 -Certificate .\certificates\phone.pem -Key .\certificates\phone-key.pem
```

Replace the example IP/files with your actual values. When you explicitly want to start it, repeat with `-Start`. It runs native Next dev on **that IP only, port 3443**, with provided HTTPS files and exact allowed host/origin. The script does not install trust or add firewall rules; review any Windows private-network firewall decision yourself. Stop with Ctrl+C. Environment values set by the helper are restored when it exits.

5. On the phone open `https://YOUR_WORKSTATION_IP:3443/record`, authenticate with username `lab` and the workspace password, and verify actual sensor availability. Keep the screen unlocked/page visible. Export/save a short test, inspect quality and independently check start/end cues before a physical pilot. CSV from phyphox remains the fallback if APIs or certificate trust are incompatible.

The installed Next CLI's HTTPS flags are a development facility, not a public hosting configuration. No LAN listener, CA installation, firewall change or physical phone verification was performed during Step 4. The shared workspace gate is not multiuser authorization. Never expose private volumes publicly; see DEPLOYMENT.
