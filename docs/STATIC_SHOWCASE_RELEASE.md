# RallySense Lab — static showcase release

> Current public acceptance: **NOT READY**. The user deployed to Cloudflare; live Chromium tests exposed media seeking and two accessibility defects. A locally verified static-only replacement awaits redeployment. See [public acceptance and replacement handoff](LIVE_PRODUCTION_ACCEPTANCE.md). The original AWS/local-only release record below is historical.

**READY — AWS ACTION REQUIRED. No live URL or AWS resources created.** Final source checkpoint is the local commit containing this document (`git log -1 --format=%H`); source-data checkpoint is `253e407e2a8bbef5f2002e3c7e67b67c658341f8`. No GitHub push. The user has requested that AWS creation remain paused until authentication and the exact Free plan are confirmed.

The separate [apps/showcase](../apps/showcase) application is Vite/React/TypeScript with hash routing. It preserves the charcoal/teal identity and provides landing, actual video replay/seek/playback speed, synchronized signal/pose/cursor, chart zoom, event navigation, ten stored Sensor Fusion Challenge cases, comparisons, timing disagreements, failure exploration, methodology and JSON/Markdown/print-to-PDF reports. No upload, capture, new inference, backend authentication or private research service is implied.

## Run and deployable output

```powershell
npm.cmd --prefix apps/showcase ci
npm.cmd --prefix apps/showcase run build
npm.cmd --prefix apps/showcase run preview
```

Open **http://127.0.0.1:14173/**. The final production preview is running on loopback at handoff; restart with the last command if needed. No Docker/database is needed to build or serve this static application. Use an HTTP server, not `file://`.

- Final site: `apps/showcase/dist/` — **28 files, 2,507,048 bytes**; JS about **84.3 kB gzip**.
- Verified handoff ZIP: `storage/static-showcase/rallysense-showcase-release.zip` — **361,971 bytes**, SHA-256 `a3024bb064e0a96892f6f7e9eb1aa12e2058ddac2e8bda388dcf7d7201e9996f`.
- Exact file hashes: [static build manifest](evidence/static-showcase/static-build-manifest.json). ZIP contains `index.html` at its root. **Extract it before S3 upload; uploading the ZIP as one object does not publish the site.** Only upload the 28 build files, never the repository, `storage/`, env files or prior release bundles.

## Provenance and verification

[Deterministic export](../scripts/export-showcase.py) reads only the fixed isolated Step 6.6 generated database, rejects wrong session IDs/non-synthetic/participant data, validates all six recorded artifact hashes and seven scored/failure results against reviewed evidence, and exports the paired fixture. No model/research algorithm runs during export. Repeated export produced identical dataset SHA-256 **`90a15516ad924837ac7531a8703d815090cac7a42ce5e7bd759513691ac05de0`**. It contains **801 IMU samples, 241 analytical pose frames, ten actual stored experiments (nine succeeded, one explicitly failed)** and the hash-verified generated 320×240 video. Three stored runs are unscored; undefined precision stays undefined. References retain **`independent=false`**. No tennis accuracy, impact timing, calibrated confidence or biomechanical reconstruction is established.

| Actual check | Result |
| --- | --- |
| Production build, TypeScript and ESLint | Passed |
| Focused unit/provenance/visualization tests | **7 passed** |
| Playwright against the final built output | **9 passed**, zero skipped/retried; desktop/mobile, video play/seek/pose/zoom, ten scenarios, comparison, downloads/PDF, hash deep links/refresh, error/retry |
| Runtime requests | Tests enforce **GET only, same-origin static paths**, no backend/external/mutating requests; no missing resources/page errors |
| Static build/privacy/license/path checks | All **28 files**, six known secret values excluded, zero matches, 20 reports match stored data; generated video matches reviewed hash |
| Packaging | All 28 ZIP entries match production SHA-256 hashes; archive integrity passed |
| Existing platform preservation | **85 original source/release hashes unchanged**; 12 private research row inventories unchanged; **139 artifacts rehashed, zero missing/mismatched**. Generated source DB stopped again, volumes retained. Existing services/history/evidence preserved. |
| Dependency audit | **0 known production dependency findings**; ten moderate findings remain in development lint tooling and are not shipped. This is not a guarantee of absence of all vulnerabilities. |
| AWS/live HTTPS | **Unexecuted**: authentication/console pricing and cost coverage pending; resource IDs/live URL **none** |

[Browser evidence](evidence/static-showcase/browser-final.json), [unit evidence](evidence/static-showcase/unit-final.json), [static checks](evidence/static-showcase/static-check-final.json), [package evidence](evidence/static-showcase/package.json). Representative desktop/mobile screenshots and PDF were inspected; local images remain ignored under `docs/evidence/static-showcase/`. Corrected setup issues are retained: unit discovery initially included Playwright tests; copy-path verification initially treated generated `index.html` as a public source file. Both final checks pass without weakening application/scientific assertions. Initial build needed explicit Node test typings, now declared. No original audit findings were removed.

No MediaPipe model/WASM/runtime, FFmpeg/FFprobe, container OS, API, database, worker, credentials, source maps or private recording is in the output. Thus the original container/model release gates were **not waived**: those components are excluded from this separate release. Actual installed React/React DOM/Scheduler/Lucide notices are shipped in `NOTICES.txt`. Physical mobile devices, Safari/Firefox and the future CloudFront endpoint remain unverified; mobile testing used Chromium viewports. Stored scenario selection does not calculate new results. Print-to-PDF uses the visitor’s browser.

## AWS: exact next actions and budget boundary

**Authentication follow-up:** `rallysense-showcase` now authenticates successfully, currently as the root identity. All checks remained read-only. The current SDK returned **zero existing flat-rate subscriptions**; this is not proof of eligibility for a new Free plan. Free Tier usage returned **no S3 allowance records**; this does not prove ineligibility, but does not establish request-cost coverage. No bucket, distribution, subscription or PrintMatch resource was created/modified. [Actual preflight](evidence/static-showcase/aws-deployment-preflight.json) and [local-only deployment intent](../infrastructure/showcase/deployment-intent.json). The cost gate remains unresolved; stop before AWS writes.

Initial CLI check: default session expired; neither existing profile authenticated. No credentials were printed or changed. User is at CloudFront’s S3-origin setup, has **not confirmed Free**, and has created no bucket/distribution. Existing PrintMatch AI resources were not modified or deleted. Complete sign-in separately with `aws login --profile rallysense-showcase`; use that dedicated profile, not a changed PrintMatch profile. Do not send keys/tokens.

**First, before any Create/Subscribe/Upload action:** [CloudFront console](https://console.aws.amazon.com/cloudfront/v4/home) → Create distribution → **Single website or app** → review the **pricing-plan selection/review** and confirm **Free, USD $0/month flat rate**, not pay-as-you-go/Pro. Console step ordering can vary; use Back if needed. Do not advance past a resource-creation confirmation merely to find the plan. If the Free option is unavailable or the price cannot be established, stop and report that screen’s non-secret wording.

AWS documents Free as a $0 plan with **1M requests/100 GB transfer** and **5 GB S3 Standard storage credits**. The credit is account-wide, not proof every S3 operation is free. AWS separately charges S3 PUT/GET/LIST requests; account-specific free allowances/credits and existing usage must be checked before promising a $0 bill. This tiny release is about 2.5 MB/28 objects, but request counts, caching and account benefits determine any remaining request charges. **No nonzero allowance is authorized.** Do not enable extra paid logs, KMS keys, WAF add-ons, domains, Route 53 zones, servers or databases. [CloudFront plan terms](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html), [S3 request pricing](https://aws.amazon.com/s3/pricing/).

**Only after the user confirms the plan and no uncovered charges**, the controlled console procedure is:

1. S3 → Create bucket: **new** unique `rallysense-showcase-<unique-suffix>`, general-purpose **S3 Standard**, Bucket owner enforced, **all four Block Public Access settings on**, default **SSE-S3**, website hosting off. No versioning/logging/replication extras. Never select an existing PrintMatch bucket.
2. Upload **contents** of `apps/showcase/dist/` at bucket root: Add files for `index.html`, `favicon.svg`, `NOTICES.txt`; Add folders for `assets`, `data`, `reports`. Do not nest everything under `dist/`. Keep private ACLs. Confirm MIME types: HTML `text/html`, JS `application/javascript` or `text/javascript`, CSS `text/css`, JSON `application/json`, MP4 `video/mp4`, MD `text/markdown`, SVG `image/svg+xml`.
3. CloudFront → new **Single website or app** distribution named `rallysense-showcase`. Skip custom domain; select the new **S3 REST bucket origin**, not a website endpoint. Origin path empty. Enable **Origin access control (recommended)** and **Sign requests (always)**. No backend/edge function or paid protection additions.
4. Confirm Free **$0/month** on the final review, then create **only this new distribution**. Apply CloudFront’s generated **read-only, distribution-scoped** bucket policy to the **new** bucket; [reviewable template](../infrastructure/showcase/bucket-policy.example.json). Keep S3 Block Public Access on. [AWS OAC instructions](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html).
5. Confirm General → **Default root object: `index.html`**. Behavior: redirect HTTP to HTTPS; GET/HEAD only; compression enabled; managed optimized caching. Prefer short caching for HTML/data/reports (e.g. 60–300 seconds) and immutable caching for hashed assets when configuring subsequent releases; no paid invalidation is needed to launch a new distribution. Default CloudFront certificate/hostname; no rewrite/function/custom error fallback is necessary for **hash routes**.
6. In the **new distribution’s plan details/Manage plan**, verify the active subscription is **Free / $0 flat rate**, not just an old generic “free tier” allowance. Record distribution ID/domain, bucket name/region, OAC ID and the actual plan. Wait until deployment finishes. No such IDs exist yet.
7. Verify `https://<actual-domain>.cloudfront.net/`, `/#/replay?t=5`, `/#/challenge`, `/#/compare`, video/JSON/downloads and mobile navigation. Direct unauthenticated S3 object access must be denied. Confirm actual public HTTPS and private-origin behavior, not just console status.
8. Run the same production suite against the real URL, and retain actual results before claiming deployment complete:

```powershell
$env:SHOWCASE_URL = 'https://REPLACE-WITH-ACTUAL-DOMAIN.cloudfront.net'
npm.cmd --prefix apps/showcase run test:e2e
Remove-Item Env:\SHOWCASE_URL
```

Until the user completes the current account/plan/cost gate, **stop cloud work**. If strict $0 AWS coverage is unavailable, the lowest nonzero AWS cost would still need new authorization; it has not been estimated as an approved spend. A $0 non-AWS alternative is a pure-static Cloudflare Pages Free direct upload (28 files fit its limits); changing providers also needs the user’s choice. [Pages Free limits](https://developers.cloudflare.com/pages/platform/limits/). Nothing was provisioned on either provider.

## Recruiter explanation

“RallySense Lab makes sparse IMU and visual motion observations inspectable on one timeline. The preserved full-stack platform supports ingestion, pose extraction, durable inference and immutable experiments; this fast static showcase presents its actual generated fixtures, precomputed associations and failure cases. The emphasis is reproducibility, synchronization and honest treatment of uncertainty—not a claim of validated tennis accuracy.”
