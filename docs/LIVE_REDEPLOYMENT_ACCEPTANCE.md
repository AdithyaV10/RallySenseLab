# Redeployed public showcase acceptance

Exact target: https://lucky-band-a550.adithya-v1833.workers.dev/

**Verdict: NOT READY.** The three original defects are fixed in the deployed replacement, but an additional live timestamp-navigation defect remains. This is public HTTPS Chromium evidence, not localhost verification.

**Final complete suite: 15 passed / 1 failed / 0 skipped, 45.1 seconds, zero retries.** All 14 original acceptance tests pass; the failure is a new, stronger same-view timestamp-navigation regression.

## Remaining confirmed defect

Open `/#/replay?t=2`, allow video to load, then change the same tab's URL to `/#/replay?t=5` without reloading. The URL changes but the video/shared clock remains at **2 seconds**, rather than seeking to 5. This reproduces while the Replay component remains mounted. Its query timestamp is captured in an initial-time ref and only applied on media initialization; subsequent query changes are not applied to the loaded video. Opening the timestamp link from another view, a fresh document, and refreshing the timestamp URL all pass.

The proposed narrow correction is to react to replay timestamp query changes and apply them to actual media (including pending metadata readiness). Preserve manual seeking and failure-explorer navigation. No application fix, rebuild or deployment was performed in this acceptance-only rerun. This defect remains unresolved on the public URL.

## Public verification

| Check | Result |
| --- | --- |
| Landing, branding, navigation, fresh incognito and HTTPS | PASS |
| Actual video play/pause, playback speed, keyboard and zoom | PASS |
| Ten repeated seeks: actual video, shared clock, pose and graph cursor | PASS |
| Failure-explorer reference links across all ten stored scenarios | PASS; every available matched/missed reference button tested and actual media time verified after settling |
| Timestamp link from another view and refresh | PASS |
| Timestamp change while replay is already mounted | FAIL: requested 5 s, actual 2 s |
| All ten scenario states, stored evaluations and three mode selectors | PASS |
| Comparisons and actual event markers | PASS |
| All 20 JSON/Markdown report files and browser export actions | PASS |
| Actual print lifecycle and Chromium PDF | PASS; physical OS print dialog not inspected |
| Desktop, 390 px phone and 820 px tablet | PASS; six major views per viewport, no horizontal document overflow |
| Both prior accessibility findings and automated contrast/label/focus checks | PASS; all 18 scans report zero violations |
| Keyboard skip link, visible focus, timeline and playback | PASS |
| Browser history, report refresh, unknown routes | PASS |
| Complete replacement manifest | PASS; 28/28 files match SHA-256, HTTPS, HTTP 200 and correct MIME; zero mismatches |
| Console/network after waiting for actual replay readiness | PASS; zero exceptions, console errors, failed or unexpected requests |
| Approved synthetic data/provenance and privacy probes | PASS within known asset/probe scope; no live inference or upload claim introduced |
| Account configuration, arbitrary unlisted assets, full assistive-technology conformance | UNVERIFIED; outside public black-box evidence |

The fixture has no unmatched output predictions to navigate; its empty state is genuine. No artificial unmatched cases or accuracy claims were introduced. Stored data and scientific algorithms were not changed.

## Evidence and test history

All runs use real Chromium at the exact public HTTPS URL, with TLS validation, no mocks, no localhost server and no retries. The replacement manifest is `docs/evidence/live-showcase/replacement/static-build-manifest.json` (28 files / 2,508,133 bytes).

- [Complete final test command and output](evidence/live-showcase/redeployed/browser-complete.json) and [detailed final test report](evidence/live-showcase/redeployed/playwright-results.json).
- [Complete deployed asset hashes](evidence/live-showcase/redeployed/public-asset-integrity.json).
- [Repeated seek synchronization](evidence/live-showcase/redeployed/public-replay-synchronization.json), [persistent failure navigation and mode selection](evidence/live-showcase/redeployed/public-persistent-failure-navigation.json), [remaining timestamp defect](evidence/live-showcase/redeployed/public-mounted-timestamp-change.json).
- [18 public accessibility/layout scans](evidence/live-showcase/redeployed/public-layout-accessibility.json), [network/console](evidence/live-showcase/redeployed/public-network-console.json), [privacy probes](evidence/live-showcase/redeployed/public-privacy-probes.json).
- Fresh public screenshots: `docs/evidence/live-showcase/redeployed/live-{landing,replay,challenge,comparison,methodology,report}-{desktop,phone,tablet}.png`. Chromium PDF is in the same directory. Image/PDF files are local ignored evidence.

The first redeployment run yielded 13 passed / 1 failed: the network audit navigated away from a replay fetch before React/media readiness, causing its AbortController to cancel that request. The audit now waits for the actual video's readyState before leaving replay; it does not exclude failed requests. The follow-up network check passes with no failures. Original output is retained in `browser-full.json` and `initial-run/`.

A strengthened run yielded 14 passed / 1 failed, exposing the already-mounted timestamp defect. Its output is retained in `browser-full-final.json` and `strengthened-run/`. The final suite separates the passing failure/deep-link/mode workflow from this failing same-view query-change regression. Historical failures have not been removed or reclassified as passes.

No Cloudflare/AWS resources, original full-stack application, scientific algorithms or research records were modified. Public deployment is confirmed to contain the replacement's assets; no claim that the remaining defect is locally or publicly fixed is made.
