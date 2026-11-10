# Final replay timestamp correction

**Local fix verified; NOT READY to share until deployed and accepted at the public HTTPS URL.** No cloud update was performed: Cloudflare credentials and a verified authenticated account/Worker were unavailable. The public site still serves `assets/index-aEXiQm6p.js`; this correction builds `assets/index-EHsTvdm9.js`.

## Exact changes

- `apps/showcase/src/main.tsx`: pass the current hash timestamp into Replay; apply timestamp changes to actual video and shared time; retain the latest pending seek for metadata readiness. Manual seeks also update that pending request. Playback ticks do not write the URL or reapply old query values. The video component/source is not remounted/reloaded for timestamp changes; Blob fetch, byte/hash verification, media lifecycle and scientific calculations are preserved.
- `apps/showcase/e2e/timestamp.spec.ts`: three real Chromium regressions for repeated mounted changes, back/forward, manual seeking and playback controls; actual throttled HTTP before metadata readiness and refresh; persistent failure-explorer navigation. Video identity, actual media time, pose, shared clock and chart coordinates are asserted. No media is mocked.
- `apps/showcase/playwright.live.config.ts`: include the new regression file in strict public acceptance. Existing original tests and assertions remain enabled; only the pre-existing intentionally mocked loading-error case stays excluded from the live suite.
- Documentation/status and `docs/evidence/timestamp-fix/`: new evidence and handoff. No backend, generated fixtures, research results, CSS or existing evidence modified.

## Actual local outcomes

| Verification | Result |
| --- | --- |
| Production build and TypeScript (`tsc --noEmit`) | PASS |
| ESLint | PASS |
| Unit suite | 7 passed |
| Complete production-preview Chromium suite | 12 passed / 0 failed / 0 skipped; 24.6 s |
| Mounted URL changes 2 → 5 → 3 → 7, without video remount | PASS |
| Browser back/back/forward/forward timestamp history | PASS |
| Ten repeated manual seeks; actual media, pose, cursor and shared clock | PASS |
| Playback/pause/speed, unrelated zoom changes, zoomed/full chart coordinates | PASS |
| Latest URL request before real metadata readiness, then refresh | PASS; actual Chromium network throttling, no response substitutions |
| Direct timestamp links, refresh and failure-explorer navigation | PASS |
| Complete static manifest and privacy/provenance verification | PASS: 28 files, 10 stored experiments, 20 reports, no secrets/model/native/backend artifacts |

The first local run was 11 passed / 1 failed: the new test incorrectly expected the full-trace cursor coordinate while zoom remained enabled. It now explicitly checks the zoomed coordinate, restores full trace and checks the full-session coordinate. No application behavior was changed to satisfy that assertion. Both run outputs are retained. The existing loading-error test intentionally mocks a dataset failure and is local-only; all timestamp/video regression traffic is real.

Evidence: [build/types](evidence/timestamp-fix/build.json), [lint](evidence/timestamp-fix/lint.json), [units](evidence/timestamp-fix/unit-tests.json), [final local browser output](evidence/timestamp-fix/browser-local-final.json), [static privacy check](evidence/timestamp-fix/static-check.json).

## Exact manual Cloudflare update

- ZIP: **`C:\RallySenseLab\storage\static-showcase\rallysense-cloudflare-timestamp-fix.zip`**.
- ZIP bytes: **362,376**.
- SHA-256: **`8f91094f9d5f8d5bb5c14d4218af280a317f306d45495c7080fa184b80e125bf`**.
- Archive contains `index.html` at its root and all 28 files, with paths and hashes verified by reopening the ZIP.
- Complete output: `apps/showcase/dist/`, **2,508,331 bytes**. [New production manifest](evidence/timestamp-fix/static-build-manifest.json).
- Changed deployed output relative to the previous replacement: `index.html` and `assets/index-EHsTvdm9.js` (replaces `assets/index-aEXiQm6p.js`). CSS and all scientific fixtures/reports/media remain byte-identical.

Use the existing Cloudflare Workers & Pages static-assets deployment workflow for **`lucky-band-a550`**, in the verified account for **`adithya-v1833.workers.dev`**. Upload this complete ZIP/output and activate the updated version on the existing URL. Do not upload just the JavaScript file, create another application, modify another Worker or change AWS resources. Do not upload the repository or private storage.

## Public acceptance after actual deployment

The [public identity check](evidence/timestamp-fix/public-deployment-status.json) confirms the old build remains active. It is an identity check, not an acceptance run. The latest actual public browser result remains **15 passed / 1 failed**, with the timestamp defect unresolved in that deployed version. No public pass is claimed for this local correction.

After deployment, run all **19 non-mocked public Chromium cases** with the new manifest and a separate evidence directory:

```powershell
$env:SHOWCASE_URL='https://lucky-band-a550.adithya-v1833.workers.dev'
$env:SHOWCASE_EXPECTED_MANIFEST='C:/RallySenseLab/docs/evidence/timestamp-fix/static-build-manifest.json'
$env:SHOWCASE_EVIDENCE_DIR='C:/RallySenseLab/docs/evidence/timestamp-fix/live'
uv run --project apps/api python scripts/record-check.py docs/evidence/timestamp-fix/live/browser-complete.json npm.cmd --prefix apps/showcase run test:e2e:live
```

This checks all new hashes and original visitor workflows, including the original mounted-component regression, the expanded history/pending-metadata tests, failure links, screenshots/layout/accessibility, exports and console/network/privacy. Only successful actual-public acceptance can change the verdict to **READY TO SHARE WITH RECRUITER**.
