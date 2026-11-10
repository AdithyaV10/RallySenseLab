# Public showcase acceptance — 2026-11-09

> Superseded by the [redeployed public acceptance](LIVE_REDEPLOYMENT_ACCEPTANCE.md): all original defects now pass on the actual public site, but one newly tested same-view timestamp-query defect remains. Final expanded suite: 15 passed / 1 failed. Historical first-deployment evidence below is preserved.

**Verdict: NOT READY.** Tested the actual HTTPS website at https://lucky-band-a550.adithya-v1833.workers.dev/ with real Playwright Chromium, fresh isolated contexts, certificate validation enabled and no mocked responses. The static-only replacement is built and locally verified, but has NOT been deployed or accepted on the public URL.

## Public results

| Visitor workflow | Result | Actual evidence / qualification |
| --- | --- | --- |
| HTTPS, fresh incognito load, landing, branding and navigation | PASS | Public HTTP 200; desktop/mobile screenshots; no storage state supplied. |
| Video playback, pause and playback speed | PASS | Actual media clock advances; keyboard play/pause and half-speed verified. |
| Seeking, repeated seeks and synchronized cursor/pose after seeks | FAIL | Seek to 5 s resets to 0; browser reports seekable interval [0,0] despite 8 s duration and fully buffered media. |
| IMU graphs, stored analytical pose, event markers and zoom | PASS | Rendered on public site; zoom toggles. Persistent event seeking is affected by the failure above. |
| Ten stored scenarios and all three inference-mode selectors | PASS | All ten states and stored evaluations match approved data; video/IMU/association selectors exercised. These select stored results, not live inference. |
| Scenario comparisons | PASS | Selection updates correct stored metrics, including undefined precision. |
| Failure explorer | FAIL | Stored failure/association/corruption evidence loads correctly, but persistent jump-to-replay synchronization fails. Unmatched and missed categories are limited to the actual fixture's recorded cases. |
| JSON and Markdown reports | PASS | All ten pairs checked against approved stored report contents; actual browser downloads also exercised. |
| Print/PDF report | PASS | Print action fires beforeprint; actual Chromium PDF generated; extracted two-page content includes experiment, scientific definition, provenance and synthetic disclaimer. Physical OS print dialog is UNVERIFIED. |
| Methodology and scientific disclaimers | PASS | Generated analytical landmarks explicitly distinguished from MediaPipe output; measured signals and associations do not claim confirmed tennis events or athlete accuracy. No advertised live uploads/inference. |
| Direct routes, refresh, browser back/forward, unknown hash route | PASS | Public report refresh/history/fallback exercised. Replay timestamp deep links FAIL under the seeking issue. |
| Desktop, 390 px mobile and 820 px tablet layout | PASS | Six major sections at each size; no document overflow; major screenshots captured. |
| Accessibility basics | FAIL | Two axe rule violations: hero accessible-name mismatch, and comparison scroll region lacks keyboard focus. Basic skip link, playback keyboard controls and visible focus exercised; automated contrast scans report no violations. This is not a full manual assistive-technology audit. |
| Console, networking, HTTPS assets, MIME and CORS | PASS | No JavaScript exceptions, console errors, failed/unexpected requests in recorded workflow. All 28 known deployed files have correct MIME, HTTPS and exact approved SHA-256. |
| Approved data/provenance and public asset privacy | PASS | Approved dataset and media hashes match; no backend, credentials, private recordings or model weights in the 28-file manifest. Six private/API/env/model probes return 404. |
| Cloudflare account configuration and exhaustive unlisted-asset enumeration | UNVERIFIED | No authenticated account access; public black-box checks do not prove account-wide security or absence of arbitrary unknown URLs. |

Automated public acceptance totals: **9 passed / 5 failed**, across the core suite (6/8) and extended suite (3/6), no retries. The five failures represent three defects, not five independent root causes. Mocked loading-error tests were intentionally excluded from the live suite, not counted as public passes. Supplemental real-browser checks cover mode selection, history/refresh, keyboard playback/zoom and PDF text. All original failed results remain recorded.

## Confirmed defects and prepared static-only fixes

1. **Release blocker — media seeking:** public `Range: bytes=0-63` returns HTTP 200 and the entire 15,839-byte MP4, without Content-Range or Accept-Ranges. Chromium cannot seek it, breaking timeline, marker, failure-link and timestamp-deep-link synchronization. The replacement fetches the same HTTPS fixture, validates its approved byte count and SHA-256, and uses a browser-local MP4 Blob URL. CSP adds only `blob:` to media-src. No server/API dependency or scientific algorithm changes.
2. **Accessibility — hero link:** its custom accessible name conflicts with visible content. Replacement uses visible link content as its name and retains the explanatory title.
3. **Accessibility — scroll regions:** replacement adds named keyboard-focusable regions and visible focus outlines to all three horizontal data tables.

The original full-stack application and research data are untouched. The synthetic dataset remains SHA-256 `90a15516ad924837ac7531a8703d815090cac7a42ce5e7bd759513691ac05de0`. All 28 original deployed assets matched the approved original manifest during this acceptance. No fabricated metrics or revised experimental results were introduced.

## Replacement verification — LOCAL ONLY

Production build/types, ESLint, seven units, and eight relevant production-preview browser tests passed. The final replacement's focused regression passed ten repeated seeks, timestamp deep-link initialization, actual play/pause, and eighteen layout/accessibility scans with zero violations. These results do **not** turn failed public tests into passes. See [replacement evidence](evidence/live-showcase/replacement/local-regression.json) and [final focused check](evidence/live-showcase/replacement/focused-final-local-only.json).

## Redeploy only this existing Cloudflare Worker

No Cloudflare credential/configuration was available to this session, so no deployment or other cloud-resource mutation was attempted.

- Ready ZIP: `storage/live-showcase/rallysense-cloudflare-fix-verified.zip` (362,326 bytes).
- ZIP SHA-256: `ad3523a15a97d69cc14b4a0a1c1cc0122e7ea558e3e61658e9f8852929571e05`.
- Complete output: `apps/showcase/dist/`, 28 files / 2,508,133 bytes. [Exact replacement manifest](evidence/live-showcase/replacement/static-build-manifest.json).
- Changed deployed files: `index.html`, `assets/index-aEXiQm6p.js`, `assets/index-CRrNUSTv.css`. Other fixture/report/media files are unchanged. Upload the **complete 28-file output**, preserving its relative paths and index.html at the root; do not upload the repository or storage directory.

In Cloudflare Workers & Pages, select the **existing `lucky-band-a550` Worker in the `adithya-v1833` workers.dev account**. Use that Worker's existing static-asset deployment/update workflow with the complete ZIP/output above, and make the new version active at its current URL. Do not create a second application, use Pages deployment commands, or modify AWS, other Workers, DNS or account settings. Dashboard button labels were not verified in an authenticated console.

If using the CLI instead, first authenticate and confirm the correct account and that this Worker already exists. From the repository root, the targeted static upload command is:

```powershell
npx wrangler deploy --name lucky-band-a550 --assets apps/showcase/dist
```

Do not run it in an unverified account: Wrangler can create a Worker if the name does not already exist there. No account-specific configuration has been guessed or committed.

After deployment, run the strict public suite using the replacement manifest:

```powershell
$env:SHOWCASE_URL='https://lucky-band-a550.adithya-v1833.workers.dev'
$env:SHOWCASE_EXPECTED_MANIFEST='C:/RallySenseLab/docs/evidence/live-showcase/replacement/static-build-manifest.json'
npm.cmd --prefix apps/showcase run test:e2e:live
```

First preserve existing `playwright-results.json` and screenshot evidence if rerunning in the same directory. The core/extended historical result copies are retained separately. Only a successful actual-public retest can change the verdict to READY TO SHARE WITH RECRUITER.

## Evidence

- [Core actual-public test report](evidence/live-showcase/playwright-core-results.json), [extended actual-public test report](evidence/live-showcase/playwright-extended-results.json).
- [Media defect](evidence/live-showcase/public-media-defect.json), [public asset hashes](evidence/live-showcase/public-asset-integrity.json), [scientific/report comparisons](evidence/live-showcase/public-scientific-provenance.json).
- [18 public layouts/accessibility scans](evidence/live-showcase/public-layout-accessibility.json), [console/network record](evidence/live-showcase/public-network-console.json), [privacy probes](evidence/live-showcase/public-privacy-probes.json).
- Screenshots are local ignored artifacts in `docs/evidence/live-showcase/`: `live-{landing,replay,challenge,comparison,methodology,report}-{desktop,phone,tablet}.png`, plus `live-seek-defect.png`. Public report PDF is `live-experiment-report.pdf`.

No claim of successful public seeking, completed deployment, comprehensive security certification, or validated tennis accuracy is made.
