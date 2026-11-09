# Final image security review — Step 6.5

**Step 6.6 update:** Read the [focused Mode A review](STEP6_6_MODE_A_REVIEW.md) and [per-finding dispositions](evidence/step6_6/residual-security-dispositions.json). New Mode A raw total is 0 critical/94 high, plus seven manually retained XML advisories absent from the Alpine feed. No security exception is approved. The original Step 6.5 findings/images and Mode B native blockers below are preserved.

2026-11-09. **Engineering review delivered; no image is security-approved.** Mode A is ready for a human security decision on its documented residual risks. **Mode B is blocked by reachable/unresolved native-media findings**, in addition to shared residual-risk decisions. No deployment, cloud provisioning, DNS change, image publication or push occurred.

## Before and after

All five final candidates were scanned with pinned Trivy 0.76.2 and the same vulnerability database updated `2026-11-09T00:56:17Z`. Original Step 6 reports and intermediate candidates remain intact. The table counts package instances, not independently exploitable vulnerabilities. API and worker share one image; the new readonly variant is shown separately and is not added to the four-component comparison.

| Component | Original critical / high | Final critical / high | Distinct high/critical IDs before → after | Final instances with scanner-listed fixes |
| --- | ---: | ---: | ---: | ---: |
| Full API / worker | 1 / 234 | **0 / 52** | 60 → 16 | 5, all embedded-SBOM Python entries |
| Readonly API / worker | New variant | **0 / 52** | 16 final | 5, same SBOM entries |
| Next.js runtime | 1 / 42 | **0 / 46** | 18 → 11 | 0 |
| PostgreSQL | 2 / 93 | **1 / 64** | 49 → 20 | 0 |
| Caddy | 0 / 2 | **0 / 1** | 2 → 1 | 0 |
| Four-component comparison | **4 / 371** | **1 / 163** | Per-image counts above; do not sum as global unique IDs | — |

[Before/after evidence](evidence/step6_5/before-after-security.json) retains exact image/archive identities, every removed/new advisory ID, versions, fix availability, each residual package instance, applicability reasoning and unapproved human status. Final full reports are [API](evidence/step6_5/final/api.trivy.json), [readonly API](evidence/step6_5/final/api_readonly.trivy.json), [web](evidence/step6_5/final/web.trivy.json), [PostgreSQL](evidence/step6_5/final/postgres.trivy.json), and [Caddy](evidence/step6_5/caddy.trivy.json). [Manifest](../infrastructure/release-manifest.json) pins image IDs, OCI configuration/platform digests, archive hashes and frozen local RC aliases.

The web high count **increased by four**. Its final maintained Node 24.22.2 runtime moves from stable bookworm to stable trixie/glibc with patched system zlib, retaining the same Node ABI. This removes the bookworm minizip source match and fixes real gz-write advisories, but introduces different util-linux source matches and system SQLite package findings. The final image has fewer distinct advisory IDs, not a lower raw high count. Compatibility was established with a production build, all nine browser workflows, both upload audit cases and all fourteen boundary/adversarial probes. This choice addresses real library exposure; it is not an attempt to optimize a scanner score.

## Implemented risk reduction

| Area | Final implementation and evidence |
| --- | --- |
| Caddy | Official maintained 2.11.9 release and official builder/runtime bases; x/net pinned to 0.62.0 with supported xcaddy dependency replacement. Go toolchain 1.27.3. Actual HTTPS, Host/SNI421, Origin403, auth401 and proxy/upload flows passed. CVE-2026-78661 disappeared; go-jose/v3 remains. |
| Native media | Signed FFmpeg 9.0.2 source, SHA-256 checked; compile only required MOV/Matroska, H.264/VP8/VP9 and trusted fixture features. Disable network protocols, codec autodetection and unrelated parsers. Actual inventory and ELF dependencies confirm no libxml2. API adds format allowlists before parsing and strips application secrets from native-child environments. A child sharing the same UID/filesystem is **not** a separate security sandbox. |
| Readonly mode | Separate API target omits FFmpeg/FFprobe and their codec runtime libraries. Generated fixtures are precomputed privately using the full image, then served with readonly artifacts and an explicit session allowlist. Actual replay, reports, comparisons and idle worker passed without native tools. |
| API packaging | Stable supported Python 3.13/glibc base, security updates, multistage dependency installation; uv/compiler/media build tools and test sources are not copied to final images. The frozen lock and `/app/src` layout are retained. Existing pytest/Ruff dependencies remain because the approved project declares them as main locked dependencies; no numerical lock changes were made merely for package counts. |
| Web tooling | Remove npm, npx, Corepack and Yarn from the final runtime. Node's active fetch remains Undici 7.30.1, distinct from the removed npm bundle. Standalone Next execution is retained. |
| PostgreSQL | Retain official PostgreSQL 17.11, Debian trixie/glibc, entrypoint, data paths, SQL behavior and health checks. Rebuild official gosu 1.20 source with maintained Go 1.27.3 and verified source hash. The upstream 1.20 binary still used Go 1.24.6; that first candidate was superseded. Twenty-six Go high/critical helper instances no longer appear. |

[Native runtime evidence](evidence/step6_5/native-runtime.json), [source/signature evidence](evidence/step6_5/ffmpeg-signature.json), [runtime equivalence](evidence/step6_5/runtime-equivalence.json), [source-component SBOM](../infrastructure/media-components.cdx.json), and the Dockerfiles support these statements. Apt updates use supported stable vendor repositories, not unstable packages or cross-ABI library substitutions. Base/source/module identities are pinned; repository security updates are not a claim of bit-for-bit future rebuild reproducibility. Deploy the verified archives rather than rebuilding unreviewed images on a host.

## Important native-component coverage gap and blockers

**Removing distro FFmpeg packages from the scanner inventory does not prove the replacement static binary has no vulnerabilities.** Its source, binary hashes, actual enabled features, original seventeen advisories and an independent current NVD CPE query are reviewed separately in [native advisory review](evidence/step6_5/native-advisory-review.json). Trivy's Debian matching does not fully cover this custom static component.

The seventeen original high FFmpeg advisory IDs largely concern disabled RASC, VobSub, NVDEC, S/PDIF, RTP/ASF, ADX/AAX, hqdn3d, CAF, PNG, subtitles, CFHD/AVI, MPEG-PS, RIST, Dirac and DASH features. One HEVC MOV-muxing advisory requires a workflow the application does not perform on uploaded input; shared helper code may still be linked, so physical absence is not claimed.

The current [NVD FFmpeg 9.0.2 query](evidence/step6_5/native-current-advisory-query.json) returned seven records beyond simply matching the old package version:

| Advisory | Actual assessment |
| --- | --- |
| CVE-2025-25468 / CVE-2025-25469 | Their referenced fix is an ancestor of release n9.0.2: official comparison has `behind_by=0` and merge base equal to fix d5873be. IAMF is also disabled. Retain broad-CPE results and the ancestry evidence. |
| CVE-2026-107675 / CVE-2026-107677 / CVE-2026-107696 | SFTP/libssh, DASH and RTSP are disabled, with no network protocols in the actual build. |
| **CVE-2026-107678** | **Mode B blocker.** Required MOV/PSSH parsing is reachable. A generated control with 32 PSSH boxes passed; a 1,651,731-byte file with 50,000 boxes consumed 20.025seconds and hit the actual20-second probe timeout, returning 415. This confirms bounded resource exhaustion on the application probe path; a central API crash was not demonstrated or claimed. |
| **CVE-2026-107676** | **Mode B blocker pending applicability/patch review.** Matroska HDR10+ serialization can disclose uninitialized native bytes. HEVC/AV1 decoders are absent, but the Matroska side-data path was not proved unreachable. An upstream fix is referenced; a compatible accepted stable release containing it was not established. |

[Bounded diagnostic](evidence/step6_5/native-pssh-risk.json) ran in a disposable512MiB/1CPU/pids64 container without network or host mounts. Its command completed, but `release_acceptance_passed=false` is intentionally retained. The20-second child timeout, clean child environment, admission limits and separate worker mitigate impact; they do not fix the parser or eliminate worker-queue starvation. No crafted input was sent to an existing research session. Mode A contains no native executables and cannot execute these workflows.

Do not cherry-pick an unreviewed patch, change scientific algorithms, weaken tests or claim a clean native scan to clear these blockers. For Mode B, obtain a supported fix with focused media regressions, or separately design/review stronger native processing isolation and an explicit residual-risk decision. This larger follow-up is not implemented or authorized as deployment here.

## Residual shared-image decisions

- **PostgreSQL libxml2:** genuinely affected stable package, including critical CVE-2026-6653 and seven high matches. Debian marks stable vulnerable with no compatible stable fix established. API images no longer contain it. PostgreSQL still supports SQL/XML; the application exposes no arbitrary SQL/XML endpoint, uses parameterized SQLAlchemy and keeps the DB private. These controls reduce application exposure; they do not make the library unaffected. An explicit human decision or supported update is required for both modes.
- **Caddy go-jose/v3 CVE-2026-116587:** vendor confirms <=3.0.5 affected, no v3 fix; v4.1.6 is a different module API. The reviewed proxy has admin off and no `acme_server`, JWK or JWT endpoint. Configuration-scoped non-reachability is a proposal requiring human review, not blanket image approval. Changing PKI/JWK/admin features invalidates it.
- **General OS source matches:** util-linux mount/namespace helpers, ACLs, systemd-homed, SQLite FTS5/changesets, infocmp and Perl/GnuPG CLI paths are not application features. Nonroot API/web, no-new-privileges, private networking, no host devices/X sockets and bounded resources are relevant controls. Installed packages remain; no broad exception was approved. Exact package versions and per-CVE vendor pages are retained in the residual evidence.
- **Five Python SBOM high instances per API variant:** msgpack, setuptools and urllib3 are not top-level importable modules in the application venv. Findings are marked `AnalyzedBy=sbom` in the base Python layer. This distinguishes them from installed app dependencies, but global/bootstrap tooling or SBOM provenance still needs disposition. They were not deleted from reports or silently exempted.

[26 primary Debian vendor records](evidence/step6_5/residual-debian-vendor-evidence.json) and the [upstream JOSE advisory](evidence/step6_5/go-jose-advisory.json) support the review. The misleading webpack title for CVE-2026-76844 was reconciled with Debian's actual zlib gz-write defect; the final patched trixie package resolves that match. [OpenVEX records](../infrastructure/release.vex.json) deliberately use `affected`/`under_investigation`, never blanket `not_affected`. They are not used as scanner suppressions. No `.trivyignore` was added.

## Approval verdict

All reported image/application checks completed before an intentional turn interruption. At final handoff Docker Desktop's Engine API was unavailable, preventing a fresh container/volume enumeration; successful stops and data hashes are recorded, and all five candidate archives were rehashed offline. This local control-plane limitation is documented in [final state](evidence/step6_5/final-local-state.json), not misreported as an application test pass or an image security finding.

**Mode A:** functional/software acceptance passed with fresh synthetic-only data and no native media runtime. Ready for human security review, conditional on explicit shared-image residual decisions and owner fixture/model/access approval. **Not authorized for public release.**

**Mode B:** functional/software acceptance passed; **not ready for release approval** because the native MOV/PSSH defect and unresolved HDR metadata path remain. Shared-image and external deployment gates also apply. Authentication does not excuse these findings, and the shared identity is not a multiuser authorization model.

Primary references: [FFmpeg security](https://ffmpeg.org/security.html), [FFmpeg stable releases](https://ffmpeg.org/download.html), [upstream PSSH fix discussion](https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/24593), [HDR metadata fix](https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/2c2f6e96e31795ae95a8f8323a493ffbc493111f), [Debian libxml2](https://security-tracker.debian.org/tracker/CVE-2026-6653), [JOSE advisory](https://github.com/go-jose/go-jose/security/advisories/GHSA-mgcc-cww5-fp2q), [supported xcaddy dependency replacement](https://github.com/caddyserver/xcaddy#command-usage), [gosu 1.20](https://github.com/tianon/gosu/releases/tag/1.20). Applicability judgments are explicitly implementation-based inferences; the recorded diagnostic is direct local evidence.
