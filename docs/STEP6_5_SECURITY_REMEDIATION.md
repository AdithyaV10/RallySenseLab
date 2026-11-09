# Step 6.5 security remediation report

2026-11-09. Starting checkpoint: `208e96dbe52d1a36670f16ae05656b6a5a700a23`, initially clean. Authorization: [Step 6.5 specification](STEP6_5_SPECIFICATION.md). **Targeted engineering remediation and review delivered; public release remains unapproved. Mode B remains blocked by native-media findings.**

## Work completed

The required Step 6 plans, acceptance/status documents, all four full original Trivy reports, existing Dockerfiles/Compose, dependency locks and regression tests were inspected. A fresh private preservation baseline was taken before changes. Existing development services/data were preserved; all mutations and ordinary browser tests ran against new disposable projects. No scientific algorithm, event definition, evaluation method, numerical dependency, migration or historical research result was changed.

Implemented:

1. Multistage API build on supported stable Python 3.13/trixie, with frozen dependencies and matching source/lock locations. Build-only uv/compiler/source dependencies are omitted from final images. Nonroot execution remains intact.
2. Signed upstream FFmpeg 9.0.2 with a narrow native feature set, no network protocols, no libxml2 and no unrelated decoder/demuxer stack. MP4 H.264, WebM VP8/VP9, browser WebM video-copy repair, video metadata/timestamps and generated fixtures remain functional. API native invocations now use format allowlists and a minimal environment without application secrets.
3. Separate readonly API image without FFmpeg/FFprobe or codec runtime libraries; fresh generated fixtures/precomputed results are prepared using the full image before switching to it. Actual readonly replay/research/export/worker behavior passed.
4. Frontend runtime strips npm/npx/Corepack/Yarn. Maintained Node 24.22.2 remains unchanged; final supported trixie/glibc runtime has patched system zlib. The same standalone output works with all browser/upload gates. Its raw high count increases despite fewer distinct advisory IDs; this is disclosed, not hidden.
5. Official Caddy 2.11.9 builder/runtime bases with maintained Go 1.27.3 and x/net 0.62.0, using supported xcaddy replacement. TLS/Host/SNI/auth/reverse-proxy policy retained.
6. Official PostgreSQL 17.11/trixie initialization/data/locale behavior retained. Official gosu 1.20 source is rebuilt with Go 1.27.3, instead of the upstream binary's old Go 1.24.6. No ABI substitutions or major DB upgrades.
7. Stable vendor security updates; five final immutable local candidate aliases, OCI/archive identities, rollback manifest, component SBOM and explicit pending/affected VEX records. Nothing was published.
8. A small operational correction: paired-backup worker-stop timeout now has300seconds of control-plane headroom for Docker's150-second stop grace. An actual loaded-host timeout was retained as failure evidence, then a new backup/restore passed. This does not implement graceful worker draining on arbitrary shutdown; the helper quiesces writers and drains jobs first.

Operational/test helpers now support an isolated `step6_5` stage, separate evidence directories and loopback regression ports 13000/18000. Original assertions, upload limits, Host/Origin policy, experimental definitions and runtime-identity enforcement were not weakened. The original runtime audit source is retained in [scripts/audit-tests](../scripts/audit-tests/test_runtime_contract.py). Screenshot/PDF exclusion now covers nested evidence directories, preserving private verification imagery outside source bundles.

## Image findings and readiness

The four original components changed from **4 critical /371 high** package instances to **1 critical /163 high**. Final API52 high, new readonly API52 high, web46 high, PostgreSQL1 critical/64 high and Caddy1 high. These include source-wide duplicates and embedded-SBOM entries, not independent exploit counts. The readonly variant is excluded from the four-component aggregate. Exact IDs, versions, removed/new advisory IDs, fix availability, vendor evidence and per-instance review are in [FINAL_IMAGE_SECURITY_REVIEW](FINAL_IMAGE_SECURITY_REVIEW.md) and [before/after JSON](evidence/step6_5/before-after-security.json).

The custom static FFmpeg binary is not fully covered by Debian package matching. A separate current NVD query and native-component review found **CVE-2026-107678**, reachable through required MP4 PSSH parsing, and unresolved **CVE-2026-107676** Matroska HDR metadata serialization. A bounded actual probe diagnostic confirmed a 1.65MB generated file consuming the 20-second limit and returning 415. That diagnostic records `release_acceptance_passed=false`; it is not a passing application-security acceptance test. No full API crash, private-data leak or exploit beyond the bounded diagnostic is claimed.

**Mode A:** software verified and ready for human security review, with no native media runtime. Human disposition of PostgreSQL XML, Caddy JOSE and remaining OS/SBOM findings, plus content/model/access approval, is still required.

**Mode B:** software verified but **not ready for release approval**. Obtain a supported native-parser fix or separately reviewed processing isolation/mitigations, then repeat affected native tests and explicitly review the HDR path. Shared-image and external deployment gates also remain. Authentication is not a waiver.

## Exact verification executed

| Check | Actual final result / evidence |
| --- | --- |
| Hardened backend | **68 passed**,0 failed/skipped;6 deprecation warnings, including migrations, runtime mismatch, deterministic history, pose capacity, readonly/private-session restrictions, media/remux and new native-secret/format/VP9 checks. [record](evidence/step6_5/backend.json) |
| Original frozen-runtime audit | **2 passed** with original assertions. [record](evidence/step6_5/original-runtime-audit.json) |
| Frontend units | **15 passed** across5 files. [record](evidence/step6_5/frontend-units.json) |
| TypeScript / ESLint / contracts | All passed. Latest production build also ran TypeScript. [types](evidence/step6_5/types.json), [lint](evidence/step6_5/frontend-lint.json), [contracts](evidence/step6_5/contracts.json) |
| Standard production browser, final Node image | **9 passed**,0 failed/skipped/flaky: sensor/camera capture, replay-cache/alignment, research/evaluation/reporting, uploads and actual permitted-clip MediaPipe worker/seek/fallback. [record](evidence/step6_5/browser-standard-final.json) |
| Original upload audit, final Node image | **2 passed**, intact CSV/video above10MiB through direct and proxied paths with successful jobs. Only target-port parameterization changed. [record](evidence/step6_5/original-upload-audit-final.json) |
| Real boundary/adversarial probes, final Node image | **14 cases passed**: exact50MiB CSV/500MiB MP4, stored hashes, plus-one413, malformed400, wrongHost/Origin403, missing guard403, third concurrent429, abort fencing, idle408 and two valid concurrent jobs. [record](evidence/step6_5/upload-boundaries-final-command.json), [details](evidence/step6_5/final/upload-boundaries-results.json) |
| Release HTTPS HTTP checks | **9 groups passed**,8app services healthy; strict private-CA chain/name verification, auth401, wrongHost/SNI421, foreign/crossOrigin403, cross-project IDs404, readonly12mutation families403, allowlist, worker idle, actual workspace writes/identity and exports. [record](evidence/step6_5/https-final-acceptance.json), [details](evidence/step6_5/release-http.json) |
| Release actual Chromium | **2 complete role workflows passed**, replay/video/graphs/comparisons/missed references/reports/mobile; actual generated-video MediaPipe worker processed78frames, detected0people. Software execution only. [record](evidence/step6_5/browser-release-final-command.json) |
| Production rendering / Caddy | Both final image configurations passed offline validation with exact Host/Origin, random credentials, health/resource/private-network/readonly assertions. [record](evidence/step6_5/production-config-final.json) |
| Operator smoke after recovery | Both roles passed strict TLS/auth/readiness/Host/Origin and demo allowlist/report checks. [record](evidence/step6_5/operator-smoke-verified.json) |
| Scientific equivalence | **11 deterministic generated conditions** produced identical660,752-byte scientific output/hash across rollback and candidate images. Python 3.13.18, NumPy 2.5.4, SciPy 1.18.1, PyArrow 26.0.0 and dependency-lock SHA-256 all match. [record](evidence/step6_5/runtime-equivalence.json) |
| Hardened workspace paired recovery | **17 table digests +14 artifact hashes matched** in a new stopped recovery project; schema remains `0003_collection_readiness (head)`. [backup](evidence/step6_5/backup-workspace-verified.json), [restore](evidence/step6_5/restore-workspace.json) |
| Candidate storage readiness |14files matched;0 missing/mismatched; nonroot unwritable503, writable ready, no remaining probes. [record](evidence/step6_5/storage-candidate-final.json) |
| Existing data preservation | All original rows across12 inventories unchanged, including 108sessions/155 experiments/22 frozen references. **139 original artifacts matched**,0 missing/mismatched. [rows](evidence/step6_5/preservation-final.json), [hashes](evidence/step6_5/storage-original-final.json) |
| Production builds and scans | Five final image builds/scans completed. Scanner success is separate from failed/pending security acceptance. [image review](FINAL_IMAGE_SECURITY_REVIEW.md), [manifest](../infrastructure/release-manifest.json) |

Private-CA browser tests use functional trust bypass only for local Chromium; separate HTTP and operator checks verify chain and hostname. New actual standard browser tests ran against disposable loopback services, not the private development database. The official MediaPipe input clip remained a private verification asset and was never seeded into the public demo. Physical phones, independent tennis ground truth, public DNS/TLS/firewall, final-host load and off-host backup delivery were not newly verified or invented.

## Preserved failures and compatibility corrections

- [Initial API build](evidence/step6_5/api-build.json), exit1: restricted PATH omitted `/usr/sbin/useradd`; use the absolute build-time executable. Corrected builds passed.
- [Initial media target](evidence/step6_5/api-media-targeted.json): **2passed/1failed** because lavfi fixtures require `wrapped_avframe` transport decoding. Enabled that fixture transport, then all3 targeted cases and the full68 test suite passed.
- [Initial Python lint](evidence/step6_5/python-lint.json) and [next lint attempt](evidence/step6_5/python-lint-final.json), exit1: import order and an unused helper import. Corrected; final checks passed.
- [First paired backup](evidence/step6_5/backup-workspace.json), exit1: Docker worker-stop exceeded the helper's180-second allowance under concurrent build load. The finally block restored writers; failed backup directory retained. A new directory with 300-second worker-stop headroom passed backup/restore. No existing database was overwritten.
- [First operator smoke](evidence/step6_5/operator-smoke-final.json), exit1: ran during intentional backup quiescence, when the workspace web service was stopped. This was verification ordering, not a bypassed auth defect. Retest after confirmed healthy restart passed.
- Initial gosu binary and bookworm web candidates were superseded after component review. Their successful build/scan results remain historical; only the final identities in the manifest are release candidates.
- **Native PSSH diagnostic remains a confirmed release-blocker result**, even though its diagnostic command exits0. No failing regression was skipped, xfailed, weakened or removed to claim approval.

## Handoff and stopping boundary

Finalization limitation after the intentional turn interruption: Docker Desktop reports starting/already running, but Engine container enumeration fails with `Docker Desktop is unable to start`. A non-destructive `docker desktop start --timeout 30` returned already running; no daemon reset, restart, prune or volume operation was performed. **Current live container/volume state could not be re-enumerated.** The completed tests,139-original-file checks, recovery and successful disposable-stack stop records predate this failure and remain valid recorded evidence; they are not presented as a fresh post-interruption runtime check. All five candidate archives were rehashed offline and still match the manifest. [Final local state](evidence/step6_5/final-local-state.json), [archive integrity](evidence/step6_5/final-archive-integrity.json), [start attempt](evidence/step6_5/docker-final-start-attempt.json). Restore a functioning local Docker Engine before another runtime rehearsal; no application or cloud action is implied.

Use [FINAL_RELEASE_CANDIDATE](FINAL_RELEASE_CANDIDATE.md) and the updated [deployment handoff](DEPLOYMENT_HANDOFF.md). Review residual decisions for Mode A; retain Mode B's native-processing block. Both require external gates and explicit future deployment authorization. No cloud/DNS/public listener/registry/GitHub action was performed. Existing development data, rollback images and all recovery/test volumes are retained; disposable test services are stopped after verification. The final local Git checkpoint records the implementation, tests, raw evidence and reports.
