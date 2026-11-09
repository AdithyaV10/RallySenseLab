# RALLYSENSE LAB - STEP 6.5
## Targeted Container Security Remediation and Final Release Image Approval

**AUTHORIZED STAGE: STEP 6.5 ONLY**

You are acting as a Principal Application Security Engineer, Linux Container Security Specialist, DevSecOps Engineer, and Senior Software Release Engineer.

Your task is to resolve the outstanding container-image security gate identified in Step 6 and prepare a reviewable, secure release candidate for RallySense Lab.

This is an implementation and verification stage, not another general architecture audit.

**Do not deploy, provision cloud infrastructure, change public DNS, publish images, or push the repository.**

## 1. Inspect the current state

Project: `C:\RallySenseLab`

Starting checkpoint: `208e96dbe52d1a36670f16ae05656b6a5a700a23`

Read:

- `docs/VULNERABILITY_REVIEW.md`
- `docs/STEP6_RELEASE_REPORT.md`
- `docs/DEPLOYMENT_HANDOFF.md`
- `docs/RELEASE_ACCEPTANCE.md`
- `docs/PROJECT_STATUS.md`
- `infrastructure/release-manifest.json`
- All four Step 6 Trivy JSON reports
- Existing Dockerfiles and Compose configurations

Inspect Git status, Docker image identities, dependency locks, and current regression tests.

Preserve all databases, recordings, experiments, fixtures, and research artifacts.

## 2. Primary objective

Reduce and resolve the security findings in the API, frontend, PostgreSQL and Caddy images through evidence-based remediation.

The existing scan reported:

- API/worker: 1 critical, 234 high package instances
- Web: 1 critical, 42 high
- PostgreSQL: 2 critical, 93 high
- Caddy: 0 critical, 2 high

These counts include repeated package findings and potentially unreachable components.

Do not treat every reported package instance as an independently exploitable vulnerability.

Equally, do not dismiss findings simply because an application is behind authentication.

## 3. Prioritize reachable security risks

Focus first on:

**A. Public gateway**

- Review Caddy's current pinned image.
- Examine go-jose and golang.org/x/net findings.
- Determine whether supported, compatible security updates exist.
- Prefer maintained official images.
- Preserve TLS, Host/SNI validation, authentication and reverse-proxy behavior.

**B. API media processing**

- Examine FFmpeg, FFprobe, libxml2 and their native dependencies.
- Identify which vulnerable libraries are actually installed and reachable.
- Investigate supported patched runtime images and packages.
- Preserve required video probing and supported media workflows.
- Evaluate eliminating unnecessary codecs, parsers and utilities without breaking required functionality.
- Avoid unsafe unsupported library replacements or ad hoc ABI substitutions.
- Where practical, further isolate native media processing from application services.

**C. Frontend image**

- Review Node runtime dependencies.
- Remove unused development/build tooling from the final runtime image.
- Investigate the bundled npm, Undici and brace-expansion findings.
- Preserve Next.js standalone execution and existing authenticated upload streaming.
- Do not confuse bundled npm dependencies with the active Node fetch runtime.

**D. PostgreSQL image**

- Investigate supported updated official images.
- Review the gosu helper and its embedded Go dependencies.
- Prefer supported compatible updates over removing required initialization behavior.
- Preserve database initialization, health checks, persistence, migrations and backup compatibility.

**E. General operating-system packages**

- Identify unnecessary installed utilities.
- Remove build-time packages from runtime stages when possible.
- Apply supported security updates.
- Minimize the attack surface.
- Preserve nonroot execution, health checks and required certificate support.

## 4. Scientific and functional integrity

Do not change RallySense Lab's sensor-fusion algorithms, event definitions, evaluation methodology or research results merely to reduce scanner findings.

Preserve:

- MediaPipe integration
- NumPy/SciPy behavior
- FFprobe validation where required
- Durable worker execution
- Frozen runtime identity enforcement
- Authenticated streaming uploads
- CSV normalization
- Pose extraction
- Scientific experiment reproducibility
- Original stored artifacts and manifests

Any dependency/runtime change must update future build identities correctly.

Existing historical results must not be rewritten.

If a numerical dependency changes, run deterministic equivalence tests and document any difference.

## 5. Build hardened candidate images

Implement supported improvements using maintainable, reproducible Dockerfiles.

Prioritize:

1. Minimal runtime packages
2. Safe supported version updates
3. Multi-stage builds where useful
4. Removal of unnecessary build tools
5. Smaller native-parser exposure
6. Pinned immutable dependency/image identities
7. Nonroot execution
8. Appropriate filesystem and privilege restrictions

Do not switch to an incompatible base image solely to lower the vulnerability count.

Do not upgrade from a supported stable distribution to an unstable distribution without establishing compatibility, maintenance and security implications.

Preserve rollback image references.

## 6. Repeat vulnerability scanning

Use the available Trivy installation or a justified compatible update.

Scan all final candidate images.

Create a before/after comparison containing:

- Image identity
- Critical findings
- High findings
- Distinct advisory IDs
- Fix availability
- Actual package/component
- Reachability assessment
- Remediation status
- Remaining risk
- Supporting vendor evidence

Retain all original scan evidence.

Do not delete historical findings.

Do not use broad `.trivyignore` entries to create an artificially clean report.

For residual findings, require specific vendor evidence, applicability reasoning, and a clearly marked human-approval status.

If VEX is appropriate, create narrowly scoped, evidence-backed VEX records. Do not automatically mark every unfixed advisory as non-exploitable.

Scanner execution success is not equivalent to security acceptance.

## 7. Test the hardened application

Run all relevant application and deployment regressions.

At minimum:

- Backend tests
- Frontend tests
- TypeScript and lint
- API contract checks
- Database migration consistency
- Production image builds
- Standard browser workflows
- Original upload audit cases
- Large upload boundary cases
- Worker runtime identity checks
- Pose capacity tests
- Storage readiness
- Replay alignment/cache tests
- MediaPipe worker and fallback
- Research experiment reproducibility
- Authentication and read-only restrictions
- Private-session isolation
- Isolated deployment smoke tests
- Backup/restore compatibility
- Existing data and artifact hash preservation

Do not weaken or skip failing acceptance tests.

If an image update causes a regression, investigate and correct it or revert that specific candidate change.

## 8. Separate release-scope assessment

Evaluate two release targets independently.

**Mode A: Curated read-only public demonstration**

- Fresh synthetic-only volumes
- Approved media and fixtures
- Precomputed experiments
- No public uploads or mutations
- Idle research worker
- Protected private services
- HTTPS authentication gateway

Investigate whether a smaller read-only release image can safely omit components unnecessary for viewing approved results, without breaking media playback or report exports.

**Mode B: Authenticated research workspace**

- Full recording uploads
- Native media validation
- Pose extraction
- Sensor processing
- Research worker
- Annotations
- Experiments and reporting

Do not approve Mode B while significant reachable media-parser risks remain unresolved or unreviewed.

Do not confuse controlled shared-workspace authentication with a multiuser security model.

## 9. Efficiency and execution rules

This task must not become an endless exploratory vulnerability audit.

Use the existing Step 6 grouping and evidence.

Prioritize security changes that materially reduce exposure.

After each candidate image modification:

1. Build the affected image.
2. Run targeted checks.
3. Rescan it.
4. Compare results.
5. Retain the change only if it provides a justified improvement without unacceptable regressions.

Avoid repeatedly rebuilding and scanning unchanged images.

Use existing test evidence when still applicable, but rerun checks affected by modified runtime images.

Work autonomously through the authorized remediation stage.

If a vulnerability has no safe available fix, document the blocker and continue independent work rather than attempting risky unsupported changes.

## 10. Required deliverables

Create:

- `docs/STEP6_5_SECURITY_REMEDIATION.md`
- `docs/FINAL_IMAGE_SECURITY_REVIEW.md`
- `docs/FINAL_RELEASE_CANDIDATE.md`

Update:

- `docs/VULNERABILITY_REVIEW.md`
- `docs/DEPLOYMENT_HANDOFF.md`
- `docs/RELEASE_ACCEPTANCE.md`
- `docs/PROJECT_STATUS.md`
- `infrastructure/release-manifest.json` if new candidate images are approved for review

The final report must clearly show:

1. Original scanner findings
2. Confirmed vulnerabilities and exposure paths
3. Changes implemented
4. New image identities and hashes
5. Updated scan findings
6. Resolved advisories
7. Remaining advisories
8. Supported residual-risk assessments
9. Exact tests executed and results
10. Regression or compatibility problems
11. Read-only demo readiness
12. Authenticated workspace readiness
13. Remaining human security decisions
14. Recommended next deployment action

Do not label images security-approved when significant unresolved risk remains.

## 11. Final stopping point

When the work is complete:

- Update all reports.
- Preserve all original data and research records.
- Create a local Git checkpoint.
- Confirm working tree status.
- Present actual before/after findings.
- State whether each release mode is ready for human security approval.
- STOP.

Do not purchase hosting.

Do not create a DigitalOcean server.

Do not publish container images.

Do not start public services.

Do not modify DNS.

Do not push the repository.

If your usage allowance runs out, preserve the checkpoint and resume this stage rather than restarting.

End with:

**STEP 6.5 COMPLETE - IMAGE SECURITY REMEDIATION REVIEW DELIVERED. AWAITING RELEASE APPROVAL.**

If significant work remains, report partial completion instead of claiming success.

**BEGIN STEP 6.5 NOW.**
