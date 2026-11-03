# Technical validation and environment evidence

Inspected 2026-11-03 (user timezone America/New_York). This records documentation/metadata checks and environment probes, not implementation tests. Recommendations are engineering decisions derived from the sources; their runtime suitability still requires Step 2 validation.

## Observed environment

| Check / command | Actual result |
| --- | --- |
| `Get-Location` | `C:\RallySenseLab` |
| `[System.Environment]::OSVersion.VersionString` | Microsoft Windows NT 10.0.26200.0 |
| `$PSVersionTable` | Windows PowerShell 5.1.26100.9711 |
| Initial `Get-ChildItem -Force`; `rg --files -g AGENTS.md -g '!node_modules' -g '!.git'` | Empty workspace, no files or AGENTS.md; rg exited 1 for no matches |
| Ancestor instruction inspection | No `C:\AGENTS.md` or workspace AGENTS.md found |
| `node --version` | v24.21.0 |
| `npm --version` | PowerShell selected npm.ps1 and blocked it under execution policy |
| `npm.cmd --version` | 11.19.0; working alternative, no execution-policy change needed |
| `python --version` | Python 3.13.9 |
| `python -m pip --version` | pip 26.1.2 for Python 3.13 |
| `py --version` | Launcher present but returned “No installed Python found!”; use working python directly |
| `uv --version` | 0.12.23 |
| pnpm / yarn discovery | Neither available on PATH; no need to add another JS manager |
| `docker --version` | Docker 29.5.2, plus access-denied warning reading user Docker config |
| `docker compose version` | Docker Compose v5.1.4, same config warning |
| `docker info --format '{{.ServerVersion}}'` | Failed: docker_engine named pipe not found; daemon unavailable in this session |
| `Get-Command ffprobe, ffmpeg, psql -ErrorAction SilentlyContinue` | No binaries found on PATH; does not prove they are absent elsewhere |
| `git --version` | 2.51.0.windows.1 |
| Initial `git rev-parse --show-toplevel` | Not a repository; dedicated empty project folder was safe to initialize |
| Git identity checks | User name/email configuration present; personal values omitted from this report |
| `git init -b main` | Successfully initialized local repository |

No runtime, dependency, Docker configuration, or system execution-policy changes were made. No containers or application servers were started. A local Git repository was created because the user explicitly requests stage checkpoints.

After Git initialization, subsequent sandboxed shell processes failed with `helper_unknown_error: setup refresh had errors` (including a simple Get-Location retry). Elevated execution worked, but Git reported that the new `.git` directory belonged to the sandbox account rather than the elevated user. Repository operations therefore use the scoped option `git -c safe.directory=C:/RallySenseLab ...`; global Git trust was not modified. This is a tooling/environment limitation, not an application failure or an automatic-approval rejection.

## Public registry metadata snapshot

Python standard-library `urllib.request` fetched npm `https://registry.npmjs.org/<name>/latest` and PyPI `https://pypi.org/pypi/<name>/json`, with 15-second timeouts and bounded concurrency. The first sandboxed attempt failed with WinError 10013 (socket access restricted). A narrowly scoped elevated read-only metadata query succeeded for all 23 packages. Nothing was installed. Metadata availability does not imply a clean dependency solve, wheel availability, security audit, or build success.

### JavaScript candidates

| Package | Reported latest | Compatibility metadata observed |
| --- | --- | --- |
| [next](https://registry.npmjs.org/next/latest) | 16.4.4 | Node >=20.9; React/React DOM peers include ^19.0.0 |
| [react](https://registry.npmjs.org/react/latest) | 19.3.1 | Compatible major per checked UI peers; match react-dom exact version after checking it |
| [typescript](https://registry.npmjs.org/typescript/latest) | 7.0.2 | Node >=16.20; Next/tooling compatibility still needs a build |
| [tailwindcss](https://registry.npmjs.org/tailwindcss/latest) | 4.3.4 | No engine/peer constraints returned in selected fields; PostCSS integration not yet resolved |
| [@mediapipe/tasks-vision](https://registry.npmjs.org/@mediapipe/tasks-vision/latest) | 1.2.0 | Runtime/model/WASM/browser combination untested |
| [recharts](https://registry.npmjs.org/recharts/latest) | 3.10.1 | Node >=18; React, React DOM, react-is peers include ^19 |
| [@tanstack/react-query](https://registry.npmjs.org/@tanstack/react-query/latest) | 5.105.3 | React and React types peers ^18 or ^19 |
| [vitest](https://registry.npmjs.org/vitest/latest) | 5.1.0 | Node ^22.12 or ^24 or >=26; Vite ^6.4/^7/^8 peers |
| [@playwright/test](https://registry.npmjs.org/@playwright/test/latest) | 1.64.1 | Node >=20 |
| [lucide-react](https://registry.npmjs.org/lucide-react/latest) | 1.67.0 | React peer includes ^19 |
| [@radix-ui/react-dialog](https://registry.npmjs.org/@radix-ui/react-dialog/latest) | 1.3.1 | React/React DOM peers include ^19 |

Installed Node 24.21.0 meets the checked engine ranges. This is only a metadata-level compatibility assessment. React DOM, react-is, Vite, DOM test environment, Testing Library, ESLint/config, OpenAPI generator, type packages, and exact Tailwind integration must be checked before installation. In particular, do not assume a new TypeScript major works with every plugin. [Next.js installation documentation](https://nextjs.org/docs/app/getting-started/installation)

### Python candidates

| Package | Reported latest | Requires Python |
| --- | --- | --- |
| [fastapi](https://pypi.org/pypi/fastapi/json) | 0.162.0 | >=3.10 |
| [pydantic](https://pypi.org/pypi/pydantic/json) | 2.14.2 | >=3.10 |
| [sqlalchemy](https://pypi.org/pypi/sqlalchemy/json) | 2.1.6 | >=3.11 |
| [alembic](https://pypi.org/pypi/alembic/json) | 1.20.1 | >=3.10 |
| [psycopg](https://pypi.org/pypi/psycopg/json) | 3.3.7 | >=3.10 |
| [numpy](https://pypi.org/pypi/numpy/json) | 2.5.4 | >=3.12 |
| [scipy](https://pypi.org/pypi/scipy/json) | 1.18.1 | >=3.12 |
| [pyarrow](https://pypi.org/pypi/pyarrow/json) | 26.0.0 | >=3.11 |
| [pytest](https://pypi.org/pypi/pytest/json) | 9.2.0 | >=3.10 |
| [uvicorn](https://pypi.org/pypi/uvicorn/json) | 0.54.0 | >=3.10 |
| [python-multipart](https://pypi.org/pypi/python-multipart/json) | 0.0.33 | >=3.11 |
| [scikit-learn](https://pypi.org/pypi/scikit-learn/json) | 1.9.1 | >=3.11; Step 3 only if needed |

Installed Python 3.13.9 satisfies these top-level Python requirements. Transitive dependency ranges and platform wheels remain unverified. Target Python 3.13 with uv lock resolution and actual imports in Step 2; any fallback version must be documented, not quietly substituted. Browser pose avoids a Python MediaPipe dependency; OpenCV, server MediaPipe, and PyTorch are deliberately not required for the initial architecture.

PostgreSQL's official policy currently lists 17.11 as supported through 2029-11-08. Use maintained 17.x for the proposed baseline, refreshing the minor/image digest during implementation. No image pull or server execution has been verified. [PostgreSQL versioning policy](https://www.postgresql.org/support/versioning/)

## Approach evidence and open checks

| Topic | Documentation finding / design implication | Still unverified |
| --- | --- | --- |
| Browser pose | VIDEO mode accepts frame timestamps; synchronous work motivates worker execution. [Google guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/web_js), [Google worker example](https://github.com/google-ai-edge/mediapipe-samples-web/blob/main/src/workers/pose-landmarker.worker.ts) | Model license/hash, current API signatures in installed version, worker delegate support, real-video output |
| MediaPipe time units | `detectForVideo` timestamp argument is milliseconds. [API reference](https://developers.google.cn/edge/api/mediapipe/js/tasks-vision.poselandmarker) | Installed runtime behavior and monotonic/retry tests |
| Frame timing/overlay | `mediaTime` describes the presented frame; presentation callbacks do not guarantee processing all source frames. [MDN callback docs](https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement/requestVideoFrameCallback) | VFR, rotation, seeking, throttling, practical overlay error |
| Phone capture | Permission and secure-context requirements vary by API/browser; rates/axes need normalization and device testing. [W3C specification](https://www.w3.org/TR/orientation-event/), [MDN permission guide](https://developer.mozilla.org/en-US/docs/Web/API/Device_orientation_events/Detecting_device_orientation) | Real iOS/Android capture, timestamp behavior, sign conventions and interruptions |
| CSV interoperability | Phyphox can export a CSV per data set and time-reference metadata; require explicit maps. [Phyphox format](https://phyphox.org/docs/file-format/) | Representative exports and locale/paused-clock fixtures |
| Time-series storage | Parquet supports columnar data and row groups; use immutable, bounded window reads. [Arrow guide](https://arrow.apache.org/docs/python/parquet/parquet.html) | File sizes, window latency, wheel/runtime compatibility |
| Peak/filter baseline | SciPy supports peak prominence/distance and SOS forward/backward filtering. [Peaks](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html), [filter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html) | Parameter suitability, edge effects, true recording behavior |
| Event matching | Assignment tooling exists; cardinality-first tolerance logic is a project-defined protocol, not an automatic property of any solver. [SciPy assignment](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) | Implementation/adversarial tests and annotation reliability |
| Grouped evaluation | Related observations must stay together under grouped validation. [scikit-learn documentation](https://scikit-learn.org/stable/modules/cross_validation.html) | Actual participant count, split feasibility, statistical power |
| Jobs | Heavy work should not rely on lightweight in-process task completion. [FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) | Crash/retry/lease behavior of proposed worker |
| Media probing | FFprobe planned for bounded file metadata inspection. [Official reference](https://ffmpeg.org/ffprobe.html) | Official page timed out twice; flags, sandboxing and version must be verified at Step 2; binary absent from PATH |

Two initial documentation URLs failed: the old phyphox wiki export page and the old Arrow flat `parquet.html` URL. Current official documentation paths above were found and read successfully. FFprobe remains the explicit inaccessible-source exception. Browser documentation and metadata availability do not remove the need to run the software.

## Dependency policy for implementation

Commit exact npm and uv locks, pin direct requirements and container/model versions as appropriate, and record integrity hashes. Install only when Step 2 is authorized. Refresh candidate metadata, resolve transitive compatibility, check security advisories, verify binaries/models, and run actual build/import tests before declaring the stack functional. Keep a platform record for Windows development and Linux containers. Do not use unversioned CDN `latest` assets in a reproducible processing run.
