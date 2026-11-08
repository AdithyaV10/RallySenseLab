# RALLYSENSE LAB - STEP 5.5
## Engineering Remediation, Regression Recovery, and Release Hardening

**AUTHORIZED STAGE: STEP 5.5 ONLY**

You are acting as a Principal Full-Stack Engineer, Backend Reliability Engineer, Security Engineer, and Release Engineering Lead.

Step 5 has been completed. Its verdict was SIGNIFICANT FIXES REQUIRED for upload-enabled deployment.

Your task is to resolve the confirmed engineering defects, preserve the existing research platform, and prepare a verifiably stable application for deployment.

**Implement, test, and verify actual corrections. Do not merely produce another assessment.**

Do not deploy, provision cloud infrastructure, or push code to GitHub.

## 1. Recover the audited state

Project location: `C:\RallySenseLab`

Latest Step 5 finalization commit: `be725ae5cb474c74c84a3d2357565facd0f6d997`

Before changing code:

1. Inspect Git status and current commits.
2. Read FINAL_AUDIT.md.
3. Read REMEDIATION_PLAN.md.
4. Read DEPLOYMENT_READINESS.md.
5. Read FINAL_TEST_REPORT.md.
6. Read KNOWN_LIMITATIONS.md.
7. Read PROJECT_STATUS.md.
8. Inspect the existing audit regression tests and production configuration.

Treat these files as the authoritative remediation requirements.

Preserve all existing user sessions, PostgreSQL volumes, source artifacts, reference annotations, immutable experiments, and previous test evidence.

Do not run destructive Docker volume resets or database migrations without verifying that existing data will be preserved.

Take an appropriate non-destructive baseline before modifications.

## 2. A01 - Repair large CSV and video uploads

**Priority: HIGH.**

The audit confirmed that valid CSV and MP4 uploads exceeding approximately 10 MiB succeed through FastAPI but fail through the Next.js request path.

The Next.js global Proxy clones or truncates request bodies at its existing limit.

Implement a secure, resource-bounded streaming upload architecture.

Requirements:

- Avoid buffering entire 500 MiB video uploads in Next.js memory.
- Preserve same-origin access.
- Preserve authentication.
- Preserve Host and Origin checks.
- Preserve backend read-only restrictions.
- Prevent clients from spoofing internal credential headers.
- Keep backend credentials exclusively on trusted server infrastructure.
- Ensure the private API cannot be bypassed through a public network port.
- Preserve uploaded bytes.
- Support abort and failure cleanup.
- Enforce file and multipart size limits.
- Enforce streaming limits even when Content-Length is absent.
- Return proper HTTP 413 responses for oversized uploads.
- Apply appropriate request timeouts and concurrency limits.

Evaluate a reverse-proxy streaming path versus a carefully isolated authenticated application route.

Choose the simplest robust solution compatible with the existing single-host Docker architecture.

Do not merely increase a 10 MiB buffer to 500 MiB without addressing memory and security implications.

Preserve working smaller uploads.

### Acceptance

The existing two failing tests in `apps/web/audit/uploads.spec.ts` must pass without weakening their assertions.

Also test:

- Valid large CSV
- Valid large MP4
- Near-limit uploads
- Over-limit uploads
- Malformed multipart
- Missing Content-Length
- Aborted uploads
- Unauthorized requests
- Invalid Origin
- Read-only mode
- Upload byte/hash preservation
- Multiple bounded concurrent requests

Measure and report relevant peak memory observations.

## 3. A02 - Enforce frozen research execution environments

**Priority: HIGH.**

The audit confirmed that a queued experiment can finish successfully even when its frozen dependency/runtime metadata disagrees with the actual worker environment.

Implement execution-time environment validation.

Requirements:

- Calculate or retrieve the actual worker's dependency identity.
- Verify numerical-library/runtime versions.
- Compare them with the frozen experiment manifest.
- Reject mismatched environments before inference.
- Return a typed, understandable mismatch error.
- Preserve the original frozen experiment and historical results.
- Record actual executor identity.
- Prevent stale queued jobs from silently running under a different release.
- Document queue-draining and deployment-upgrade behavior.

Review the legacy inference path for equivalent problems.

Do not silently modify old manifests to match the current worker.

Do not change existing detector mathematics merely to satisfy these tests.

### Acceptance

Both existing tests in `apps/api/audit/test_runtime_contract.py` must pass.

Verify that:

- Matching environments execute normally.
- Mismatched environments fail clearly.
- Existing completed experiments remain unchanged.
- Deterministic numerical results remain unchanged for matching environments.
- Failure states and worker recovery behave correctly.

## 4. A03 - Repair pose extraction capacity

**Priority: MEDIUM.**

The audit identified a mismatch between browser extraction batching and the backend's maximum accepted batch indices.

The current implementation fails after 100 batches of 100 observations.

Implement a consistent bounded ingestion contract.

Requirements:

- Support at least 18,000 pose observations through ordinary staged ingestion, or explicitly enforce a smaller, documented product limit before expensive extraction begins.
- Preserve monotonic timestamp checks.
- Enforce request-size bounds.
- Handle idempotent retries.
- Handle duplicate/conflicting batches.
- Prevent unbounded memory growth.
- Reject incomplete tracks appropriately.
- Preserve existing successful pose artifacts.

Do not simply remove all numerical bounds.

Verify both short and long extraction workflows.

## 5. A04 - Repair storage readiness reporting

**Priority: MEDIUM.**

The existing readiness endpoint can report success when artifact storage is not writable.

Implement mode-aware storage verification.

For writable operation:

- Test a bounded temporary write.
- Read back the written content.
- Remove the temporary artifact safely.
- Detect permission and disk-space failures.
- Report readiness without exposing sensitive paths.

For read-only operation:

- Verify that approved fixture storage is actually readable.
- Do not require write permission unnecessarily.

Distinguish API readiness from worker readiness and processing capacity.

Add regression tests.

## 6. A05 - Correct replay cache invalidation

**Priority: MEDIUM.**

Saving a new synchronization offset can leave the displayed zoomed sensor window stale until the page is refreshed.

Correct the query identity or invalidation mechanism.

Requirements:

- Include the relevant synchronization revision or offset in cached sample identity.
- Update the graph immediately after saving alignment.
- Preserve old experiment revisions.
- Handle positive offsets.
- Handle negative offsets.
- Handle empty or partially covered windows.
- Preserve correct timeline behavior.

Reproduce the existing failure and verify the fix through a browser regression.

For a session window of [4,6] seconds and an offset of +1 second, the correct source window is [3,5] seconds.

## 7. Preserve A06 and evaluate A07

The Step 5 audit already corrected the source cancellation/retry terminal-state defect.

Preserve that correction.

Rerun its regression tests.

For the remaining dependency advisories:

- Inspect the actual dependency graph.
- Apply compatible updates when safe.
- Avoid blind major-version downgrades.
- Preserve reproducible lockfiles.
- Run lint, types, builds, and tests afterward.
- Document any unresolved advisory and its exposure.

Do not treat development-only advisories as automatically equivalent to exploitable production vulnerabilities.

## 8. Release hardening

After completing A01-A05, review the application against the original deployment readiness checklist.

Cover:

- Authentication boundaries
- Private API access
- Read-only versus writable modes
- Session access restrictions
- File upload limits
- Request rate and concurrency controls
- Worker resource limits
- Database migrations
- Persistent artifact storage
- Health checks
- Secret handling
- Logging
- Container configuration
- Restart behavior
- Backup/restore compatibility

Prepare two clearly distinguished release modes:

**Mode A: Curated read-only demonstration**

Visitors can explore approved synthetic sessions and previously computed research results.

No unauthorized uploads or mutations are allowed.

Private local recordings must not be present in the public fixture volumes.

**Mode B: Authenticated research workspace**

Authorized users can import recordings, run inference, create experiments, edit annotations, and export results.

This is a controlled workspace, not an open anonymous multiuser service.

Do not claim production-grade multiuser isolation without implementing it.

Both modes must have appropriate backend enforcement.

## 9. Full regression verification

Run the complete ordinary test suite and all Step 5 audit gates.

Required verification includes:

- Backend tests
- Frontend tests
- TypeScript
- ESLint
- Ruff
- OpenAPI contract checks
- Alembic consistency
- Production Docker builds
- Standard Playwright workflows
- Previously failing large-upload tests
- Previously failing runtime-environment tests
- Pose-capacity regression
- Storage-readiness regression
- Replay-cache regression
- Scientific numerical tests
- Read-only access checks
- Session and artifact preservation
- Restart and persistence checks

Do not mark failing assertions as skipped or expected failures.

Do not remove tests simply to make the suite green.

If any test fails, investigate the underlying cause.

Verify that previous Step 2, Step 3, and Step 4 functionality remains operational.

Preserve all existing research data and immutable results.

## 10. Operational release preparation

Prepare the project for a single-host Linux Docker deployment.

Provide or verify:

- Reviewed production Compose configuration
- Appropriate HTTPS reverse-proxy configuration
- Private database/API networking
- Environment variable templates
- Secret requirements
- Storage mounts and permissions
- Resource and request limits
- Migration instructions
- Backup and restore procedure
- Rollback procedure
- Image scanning instructions
- Operational smoke tests
- Monitoring and health checks

Do not expose a deployment endpoint or provision a server.

Do not hardcode passwords or tokens.

Do not commit private data.

If a production feature requires external credentials or infrastructure, document it rather than inventing a successful result.

## 11. Final documentation and handoff

Create:

- `docs/STEP5_5_REMEDIATION_REPORT.md`
- `docs/RELEASE_ACCEPTANCE.md`
- `docs/DEPLOYMENT_EXECUTION_PLAN.md`

Update:

- FINAL_AUDIT.md with remediation status, preserving the original findings
- REMEDIATION_PLAN.md
- DEPLOYMENT_READINESS.md
- KNOWN_LIMITATIONS.md
- TESTING.md
- PROJECT_STATUS.md
- DECISIONS.md when applicable

The final report must identify:

1. Every defect addressed
2. Exact code changes
3. Original reproduction
4. Corrected behavior
5. Regression tests
6. Remaining defects
7. Remaining deployment blockers
8. Security limitations
9. Resource and memory observations
10. Recommended production configuration
11. Required human verification
12. Exact deployment preparation instructions

## 12. Mandatory stop

Once the remediation and all feasible verification are complete:

- Create a local Git checkpoint.
- Confirm the working tree status.
- Record actual test results.
- Preserve existing volumes and data.
- Provide the full implementation report.
- STOP.

Do not deploy.

Do not push to GitHub.

Do not provision paid cloud infrastructure.

Do not claim readiness if required acceptance tests remain failing.

If a usage limit interrupts the work, preserve the current state and resume this same Step 5.5 stage rather than restarting it.

Conclude with:

**STEP 5.5 COMPLETE - REMEDIATION AND RELEASE ACCEPTANCE DELIVERED. AWAITING DEPLOYMENT AUTHORIZATION.**

If required work remains incomplete, explicitly report partial completion instead.

**BEGIN STEP 5.5 NOW.**
