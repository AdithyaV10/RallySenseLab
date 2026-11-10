# RallySense Lab static showcase

Separate Vite / React / TypeScript application. All browser requests are for local static assets; there is no backend, authentication token, upload or inference service.

From the repository root, with Node 24:

```text
npm --prefix apps/showcase ci
npm --prefix apps/showcase run build
npm --prefix apps/showcase run preview
```

Open **http://127.0.0.1:14173/**. Production output is `dist/`; hash routes work without server rewrites. Do not open the HTML via `file://`.

```text
npm --prefix apps/showcase run typecheck
npm --prefix apps/showcase run lint
npm --prefix apps/showcase run test
npm --prefix apps/showcase run test:e2e
```

The committed synthetic JSON/video/reports are sufficient to build. Re-exporting is optional: `scripts/export-showcase.py` reads only the retained isolated Step 6.6 generated database with exact fixture/artifact guards. It does not access the private research DB, start HTTP/workers or run inference. `scripts/showcase-notices.mjs` preserves installed runtime licenses. `scripts/verify-showcase-static.py` verifies the exact production assets; `scripts/package-showcase.py` creates a local checked ZIP and refuses overwrite.

Current status, actual test evidence, AWS budget gate and controlled deployment steps: [STATIC_SHOWCASE_RELEASE](../../docs/STATIC_SHOWCASE_RELEASE.md).
