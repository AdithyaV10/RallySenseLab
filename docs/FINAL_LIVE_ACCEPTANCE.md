# Final public production acceptance — 2026-11-09

**READY TO SHARE WITH RECRUITER.** The actual public HTTPS deployment passed the complete prepared suite: **19 passed / 0 failed / 0 skipped / 0 flaky, zero retries, 56.7 seconds**. Executed 2026-11-10 03:42:44 UTC (2026-11-09 22:42:44 America/New_York).

Target: https://lucky-band-a550.adithya-v1833.workers.dev/

Real Playwright Chromium, fresh isolated contexts, TLS validation enabled, no localhost/webServer fallback, no response mocks. The pre-existing intentionally mocked loading-error test is excluded from public acceptance; all 19 prepared real-public cases executed. The pending-metadata regression uses real Chromium network throttling, not synthetic media responses.

| Public feature | Result |
| --- | --- |
| Complete deployed asset identities | PASS: 28/28 SHA-256 hashes match the timestamp-fix manifest; HTTPS, HTTP 200 and correct MIME |
| Mounted replay `t=2` → `t=5` | PASS: actual video reaches 5 seconds without remounting |
| Repeated URL changes 2 → 5 → 3 → 7 and back/forward history | PASS |
| Latest timestamp before real metadata readiness | PASS |
| Direct timestamp links and refresh | PASS |
| Ten repeated seeks, actual video/shared clock/analytical pose/graph cursor | PASS |
| Play/pause, speed, keyboard controls and zoom/full-trace coordinates | PASS |
| Failure explorer | PASS: all 12 available matched/missed reference links across the ten fixtures seek settled actual media; no fabricated unmatched output cases |
| Ten stored scenarios, actual values and all three mode selectors | PASS |
| Scenario comparisons and stored event markers | PASS |
| Downloads and reports | PASS: all 20 JSON/Markdown files match approved data; browser download actions, real print lifecycle and Chromium PDF pass |
| Landing, scientific labels, navigation, history, unknown routes and report refresh | PASS |
| Desktop, 390 px phone and 820 px tablet | PASS: six major views each; no document overflow |
| Accessibility basics, including both original defects | PASS: 18 scans, zero violations; keyboard skip link, focus and timeline/playback verified |
| Console/network | PASS: zero JavaScript exceptions, console errors, failed requests or unexpected requests in the recorded workflow |
| Privacy and provenance | PASS within known manifest and public-probe scope; synthetic fixture data and generated analytical pose labels preserved; no live inference/upload or validated tennis-accuracy claim |

The active JavaScript is **`assets/index-EHsTvdm9.js`**. The release manifest contains 28 files / 2,508,331 bytes and the unchanged approved dataset SHA-256 `90a15516ad924837ac7531a8703d815090cac7a42ce5e7bd759513691ac05de0`.

## Exact invocation and evidence

```powershell
$env:SHOWCASE_URL='https://lucky-band-a550.adithya-v1833.workers.dev'
$env:SHOWCASE_EXPECTED_MANIFEST='C:/RallySenseLab/docs/evidence/timestamp-fix/static-build-manifest.json'
$env:SHOWCASE_EVIDENCE_DIR='C:/RallySenseLab/docs/evidence/timestamp-fix/live'
uv run --project apps/api python scripts/record-check.py docs/evidence/timestamp-fix/live/browser-complete.json npm.cmd --prefix apps/showcase run test:e2e:live
```

- [Exact command/output, exit 0](evidence/timestamp-fix/live/browser-complete.json), [full 19-case result](evidence/timestamp-fix/live/playwright-results.json).
- [Complete public hashes](evidence/timestamp-fix/live/public-asset-integrity.json), [expected manifest](evidence/timestamp-fix/static-build-manifest.json).
- [Mounted timestamp: requested 5 / actual 5](evidence/timestamp-fix/live/public-mounted-timestamp-change.json), [repeated seek clocks/cursors](evidence/timestamp-fix/live/public-replay-synchronization.json), [12 settled failure links](evidence/timestamp-fix/live/public-persistent-failure-navigation.json).
- [18 layout/accessibility scans](evidence/timestamp-fix/live/public-layout-accessibility.json), [network/console](evidence/timestamp-fix/live/public-network-console.json), [public privacy probes](evidence/timestamp-fix/live/public-privacy-probes.json), [stored scientific/report data](evidence/timestamp-fix/live/public-scientific-provenance.json).
- Fresh actual-public screenshots and PDF are local ignored artifacts in `docs/evidence/timestamp-fix/live/`, including `live-{landing,replay,challenge,comparison,methodology,report}-{desktop,phone,tablet}.png` and `live-experiment-report.pdf`.

No remaining defect was observed in the tested visitor workflows. This acceptance is for the static synthetic recruiter showcase. It is not a full manual assistive-technology certification, a physical OS print-dialog test, an exhaustive search for arbitrary unlisted URLs, or authenticated Cloudflare account/security verification. It does not approve the preserved full-stack application or Mode B for public deployment.

All earlier failures and local-only evidence remain preserved. This actual-public result supersedes the earlier NOT READY verdicts. No application changes, deployment, cloud-resource modification or GitHub push occurred during this acceptance run.
