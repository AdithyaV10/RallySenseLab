# Architecture decision record

Accepted for planning on 2026-11-03. None implies implemented or benchmarked functionality. Change decisions explicitly when implementation evidence warrants it.

| ID | Decision | Reason and tradeoff | Revisit when |
| --- | --- | --- | --- |
| ADR-001 | Next.js + FastAPI modular monorepo | Matches requested stack and separates interactive browser work from numerical Python; two runtimes add setup cost | Actual integration/build evidence exposes incompatibility |
| ADR-002 | Browser MediaPipe worker is primary pose path | Reduces server inference load and fits client-side preference; browser/session interruption and frame coverage require explicit handling | Long clips or reproducible exhaustive decoding require a server pipeline |
| ADR-003 | Source clocks plus revisioned microsecond mapping | Prevents silent origin/unit confusion and preserves historical run reproducibility; revisions complicate cache/UI state | Precision/range requirements change |
| ADR-004 | PostgreSQL metadata, immutable Parquet/files for dense data | Avoids SQL sample-row explosion while retaining relational constraints and efficient column/time reads; filesystem/DB recovery must be designed | Measured scale exceeds single-host storage |
| ADR-005 | One durable PostgreSQL job worker | Retry/restart/cancel state without Redis or distributed infrastructure; moderate polling/lease complexity | Measured concurrency needs exceed this design |
| ADR-006 | IMU analytical baseline before trained models | Real calculable behavior without unavailable training data; fixed parameters have limited generalization | Labeled data with adequate grouped splits exists |
| ADR-007 | Blinded human event references, explicit proxy hypotheses | Gyro peaks and pose estimates are not impact or biomechanical truth; annotation uncertainty limits conclusions | Pilot shows the selected reference cannot be labeled reliably |
| ADR-008 | Cardinality-first, minimum-error event matching | Avoids greedy matching errors and one prediction matching multiple labels; evaluator needs adversarial tests | Event definition changes to intervals or multi-class structure |
| ADR-009 | Manual offset first; drift/fusion/evaluation in Step 3 | Keeps MVP end-to-end while preserving scientific extensions | Step 3 authorization and alignment evidence |
| ADR-010 | Loopback-only single-user MVP | Avoids pretending local UUIDs provide multiuser isolation; public demo requires auth/ownership/retention review | Explicit public deployment design and authorization |
| ADR-011 | Versioned provenance for observations/features/predictions/labels/fixtures/results | Enables honest synthetic demonstration and reproducible comparisons; adds manifest/schema work | Never remove the separation; evolve schemas as needed |
| ADR-012 | npm + uv; no dependencies installed in Step 1 | Available tools, conventional locks, architecture-only scope; full compatibility remains an implementation check | Resolver/build evidence warrants versions or manager changes |
| ADR-013 | PostgreSQL 17 target with maintained patch selected later | Supported conservative baseline; pin digest after checking registry and runtime | Step 2 dependency resolution or support policy changes |
| ADR-014 | Synthetic demo uses ordinary pipelines and optionally programmatic animation | Hardware-free reproducibility; no real-video inference validation from artificial skeletons | Licensed real demo recording available |
| ADR-015 | Local requested repository, no Sites registration/hosting | User mandates Next.js/Python/PostgreSQL and no publication; hosting workflow is not needed for planning | A separately authorized deployment task chooses hosting |

The Sites skill was inspected for applicability; its implementation/publishing workflow was not invoked because the authorized stage is documentation-only. No Site was created, registered, synchronized, or published.

## Decision invariants

- Positive IMU offset moves sensor events later relative to video; inverse mapping subtracts the offset.
- Changing alignment/configuration/labels creates a new revision and never silently changes old experimental results.
- Nonfinite/missing samples never become zero and never cross large gaps through implicit interpolation.
- Missing input is distinguishable from a successful detector returning no events.
- A score, quality indicator, confidence interval, and annotation uncertainty are different concepts.
- No metric or user-facing claim may imply a real experiment when only synthetic fixtures have run.
- A completed stage always stops at its mandatory gate. Publication and Git push remain unauthorized.
