"""Record runtime package evidence and assign every scanned high/critical instance a review group.

These groups are triage, not VEX suppressions, exploit proofs or release approvals.
"""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

root = Path("docs/evidence/step6")


def docker(*args, code=None):
    if "--reuse-runtime-evidence" in sys.argv:
        prior = json.loads((root / "runtime-package-review.json").read_text())
        if "dpkg-query" in args:
            return prior["api_media_versions"]
        if "dpkg" in args:
            return prior["web_zlib_files"]
        return json.dumps(prior["api_python" if "python" in args else "web_node"])
    result = subprocess.run(
        ["docker", *args],
        input=code,
        text=True,
        capture_output=True,
        check=True,
        encoding="utf-8",
        timeout=60,
    )
    return result.stdout.strip()


runtime = {
    "web_node": json.loads(
        docker(
            "exec",
            "rallysense-step6-workspace-web-1",
            "node",
            "-p",
            "JSON.stringify({node:process.version,fetch_undici:process.versions.undici})",
        )
    ),
    "api_python": json.loads(
        docker(
            "exec",
            "-i",
            "rallysense-step6-workspace-api-1",
            "python",
            "-",
            code="import importlib.util,json\nprint(json.dumps({p:(s.origin if (s:=importlib.util.find_spec(p)) else None) for p in ['fastapi','numpy','msgpack','urllib3','setuptools']}))\n",
        )
    ),
    "web_zlib_files": docker(
        "exec", "rallysense-step6-workspace-web-1", "dpkg", "-L", "zlib1g"
    ),
    "api_media_versions": docker(
        "exec",
        "rallysense-step6-workspace-api-1",
        "dpkg-query",
        "-W",
        "ffmpeg",
        "libxml2",
    ),
    "scope": "Runtime resolution and installed package evidence; does not prove absence from every image layer or transitive binary.",
}
(root / "runtime-package-review.json").write_text(
    json.dumps(runtime, indent=2), encoding="utf-8"
)
rows = []
for name in ["api", "web", "postgres", "caddy"]:
    report = json.loads((root / f"{name}.trivy.json").read_text())
    for result in report.get("Results", []):
        target = result["Target"]
        for finding in result.get("Vulnerabilities", []):
            if finding["Severity"] not in ["HIGH", "CRITICAL"]:
                continue
            package, vid = finding["PkgName"], finding["VulnerabilityID"]
            group = "OS_REVIEW_PENDING"
            disposition = "Not cleared: assess exact installed component, prerequisites and vendor patches; no blanket not-reachable claim."
            if vid == "CVE-2023-45853" and name == "web" and package == "zlib1g":
                group = "DEBIAN_MINIZIP_SOURCE_MAPPING"
                disposition = "Vendor says bookworm src:zlib does not build affected contrib/minizip; installed zlib file inventory recorded. Source-level false-positive candidate, not blanket zlib exemption."
            elif package == "libxml2":
                group = "XML_PARSER_REVIEW_REQUIRED"
                disposition = "Stable vendor package affected. API media format probing occurs before container validation; upload reachability not excluded. PostgreSQL XML not used by app but package remains."
            elif (
                package.startswith(("libav", "libsw", "libpostproc"))
                or package == "ffmpeg"
            ):
                group = "UPLOAD_MEDIA_PARSER_REVIEW_REQUIRED"
                disposition = "Upload ffprobe parsing makes media libraries security-relevant. Readonly mode blocks upload jobs; workspace needs patched image or justified codec-specific disposition."
            elif "usr/local/bin/gosu" in target:
                group = "GOSU_EMBEDDED_GO_STDLIB"
                disposition = "gosu uid-switch helper, not app TLS server; reviewed upstream main has no networking/TLS imports. Limited exposure inference; update helper or provide reviewed per-CVE VEX."
            elif "node_modules/npm/" in finding.get("PkgPath", ""):
                group = "NPM_BUNDLED_TOOLING"
                disposition = "npm CLI dependency, not Next request import. Runtime Node fetch uses Undici 7.30.1. Remove/update unused CLI tooling; retain raw finding."
            elif package in ["msgpack", "setuptools", "urllib3"] and name == "api":
                group = "SBOM_TOOLING_NOT_IN_APP_VENV"
                disposition = "Third-party SBOM finding; module is not importable in actual app venv. SBOM/image layer provenance requires cleanup or formal disposition; not claimed installed app dependency."
            elif name == "caddy":
                group = "GATEWAY_TRANSITIVE_REVIEW_REQUIRED"
                disposition = "Configured reverse proxy accepts no JWK/JWT or HTML parser input by design. Indirect reachability not formally proven; update patched dependency or obtain reviewed disposition."
            elif package in [
                "apt",
                "libapt-pkg6.0",
                "libapt-pkg7.0",
                "gpgv",
                "dpkg",
                "dpkg-dev",
            ]:
                group = "MAINTENANCE_TOOLING_REVIEW_REQUIRED"
                disposition = "Package/signature maintenance path; no app subprocess uses package manager. Available updates should be applied and rescanned before release."
            elif (finding.get("Title") or "").startswith(
                "util-linux:"
            ) or package == "libacl1":
                group = "LOCAL_PRIVILEGED_FILESYSTEM_HELPERS"
                disposition = "Advisory prerequisites involve mount/nsenter/partition or ACL filesystem manipulation. App does not invoke these helpers; nonroot API/web and no-new-privileges reduce exposure. Not a container-escape proof; minimize tools and review any host/device/capability changes."
            elif package in ["libsystemd0", "libudev1"]:
                group = "SYSTEMD_HOMED_SOURCE_MAPPING"
                disposition = "Advisory names systemd-homed home-record signature verification. Containers do not run systemd-homed or provide user home management. Source-package match needs vendor component disposition; no blanket libsystemd suppression."
            elif package.startswith(("libx11", "libxi", "libxrender")):
                group = "X_SERVER_CLIENT_DEPENDENCIES"
                disposition = "Advisory requires malicious X-server replies; release containers have no X server/socket mount or DISPLAY integration. MediaPipe executes in browser, not server X11. Retain finding and minimize unused native dependencies."
            elif package in [
                "libcjson1",
                "libexpat1",
                "libsndfile1",
                "libtiff6",
                "zlib1g",
            ]:
                group = "ADDITIONAL_NATIVE_PARSER_REVIEW_REQUIRED"
                disposition = "Native JSON/XML/audio/image/compression parser. Potential indirect media/runtime use must be traced before clearance; language-level JSON handling alone does not clear native dependencies. Patch or obtain exact-function/vendor disposition."
                if vid == "CVE-2026-76844":
                    disposition = "Scanner associates zlib with a webpack-dev-middleware title: advisory identity/package mapping needs primary-vendor reconciliation. No false-positive suppression is approved."
            elif package == "libsqlite3-0":
                group = "SQLITE_OPTIONAL_FEATURES"
                disposition = "Application uses PostgreSQL, not FTS5 indexes or SQLite session changesets. No upload accepts a SQLite database. Native transitive uses remain unproven; source feature/version disposition or update required."
            elif package.startswith(("perl", "libperl")) or package in [
                "dirmngr",
                "gnupg",
                "gnupg-l10n",
                "gpg",
                "gpg-agent",
                "gpgconf",
                "gpgsm",
                "gzip",
            ]:
                group = "UNUSED_CLI_PARSER_TOOLING"
                disposition = "Advisory involves Perl tar, TPM/GnuPG or gzip LZH parsing, not a configured HTTP feature. API ingestion uses Python csv/JSON and ffprobe; backup uses tar without LZH decompression. Minimize/update CLI tools; no blanket exemption for compromised-container execution."
            elif package in [
                "libncursesw6",
                "libtinfo6",
                "ncurses-base",
                "ncurses-bin",
            ]:
                group = "TERMINAL_LIBRARY_DEPENDENCIES"
                disposition = "Noninteractive container entry points do not run an attacker-configured terminal workflow. Exact ncurses function/input prerequisites are not proven unreachable in all binaries; retain for update or focused vendor disposition."
            rows.append(
                {
                    "image": name,
                    "target": target,
                    "package_path": finding.get("PkgPath"),
                    "id": vid,
                    "package": package,
                    "installed": finding["InstalledVersion"],
                    "fixed": finding.get("FixedVersion"),
                    "severity": finding["Severity"],
                    "title": finding.get("Title"),
                    "primary_url": finding.get("PrimaryURL"),
                    "review_group": group,
                    "disposition": disposition,
                    "release_exception_approved": False,
                }
            )
output = {
    "security_gate_passed": False,
    "scope": "Every raw HIGH/CRITICAL package-instance retained. Groups prioritize review; no blanket CVE suppression or human risk acceptance.",
    "groups": dict(Counter(row["review_group"] for row in rows)),
    "instances": rows,
}
(root / "vulnerability-triage.json").write_text(
    json.dumps(output, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {
            "high_critical_instances": len(rows),
            "groups": output["groups"],
            "release_gate_passed": False,
        }
    )
)
