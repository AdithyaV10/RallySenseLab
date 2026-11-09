"""Per-finding residual dispositions. No scanner filtering or risk acceptance."""

import json
from pathlib import Path

root = Path("docs/evidence/step6_6")
vendor = json.loads(
    Path("docs/evidence/step6_5/residual-debian-vendor-evidence.json").read_text()
)
groups = {
    "CVE-2026-76642": (
        "configuration-limited exposure",
        "Privileged mount helper/post-hook path. API/web nonroot, no SYS_ADMIN, no-new-privileges; readonly API rootfs and artifacts RO. No application mount operation. A host/container privilege change invalidates this assessment.",
    ),
    "CVE-2026-78408": (
        "configuration-limited exposure",
        "nsenter cgroup authority requires local process/privilege conditions. No shell/namespace API; no SYS_ADMIN, no-new-privileges. Not a universal non-reachability proof.",
    ),
    "CVE-2026-78409": (
        "configuration-limited exposure",
        "Privileged X-mount.subdir symlink resolution; no mount operations or untrusted artifact writes in Mode A; capability and nonroot restrictions apply.",
    ),
    "CVE-2026-78410": (
        "configuration-limited exposure",
        "Privileged restricted bind mount ownership redirection; no mount interface, host devices or privileged containers. Same invalidation conditions as other util-linux issues.",
    ),
    "CVE-2026-54369": (
        "configuration-limited exposure",
        "ACL symlink traversal can affect privileged file operations. API/web nonroot with no privilege escalation; no untrusted filesystem writes or ACL feature in readonly application. Indirect exposure after another compromise remains possible.",
    ),
    "CVE-2026-16742": (
        "configuration-limited exposure",
        "Vendor defect names systemd-homed home-record signature verification. Shared-source libsystemd/libudev package findings do not establish vulnerable daemon operation. No homed service, D-Bus or home-management HTTP feature configured.",
    ),
    "CVE-2025-69720": (
        "configuration-limited exposure",
        "Vendor identifies infocmp analyze_string CLI overflow, not all ncurses library calls. No terminal/terminfo input endpoint or infocmp execution in Mode A. Keep raw library/source-package hits visible.",
    ),
    "CVE-2026-9538": (
        "configuration-limited exposure",
        "Vendor identifies Perl Archive::Tar header parsing. Application uses Python/OS tar only for trusted operator backups; no Perl archive upload feature. Source-package attribution alone is insufficient to prove executable reachability.",
    ),
    "CVE-2026-119373": (
        "plausible indirect exposure",
        "SQLite FTS5 detail=none negative-rowid prefix MATCH heap corruption. Public application DB is PostgreSQL; Python sqlite3 remains installed. No FTS5/import-SQLite endpoint found; another code path or future feature could expose it.",
    ),
    "CVE-2026-119374": (
        "plausible indirect exposure",
        "Corrupt SQLite FTS5 secure-delete index heap corruption. No SQLite database ingestion or FTS feature configured; library remains present, so no blanket not-affected claim.",
    ),
    "CVE-2026-119379": (
        "plausible indirect exposure",
        "Crafted SQLite session changeset parsing; no changeset API or SQLite application DB. Library still present; runtime symbol/call-chain non-reachability not fully proved.",
    ),
    "CVE-2026-116587": (
        "configuration-limited exposure; indirect CA path insufficiently established",
        "go-jose/v3 3.0.5 remains linked in Caddy. Active gateway has reverse_proxy + local health, admin off, strict SNI, no JWT/JWK/acme_server handler. This limits direct HTTP JWK input; automatic public ACME/renewal paths were not exercised or exhaustively traced. v3 upstream has no patched release; v4.1.6 is a different API and cannot be substituted blindly.",
    ),
}
instances = []
for name, sub in [
    ("api_readonly", ""),
    ("web", ""),
    ("caddy", ""),
    ("postgres", "maintained-helper/"),
]:
    report = root / f"{sub}{name}.trivy.json"
    data = json.loads(report.read_text())
    for r in data.get("Results", []):
        for v in r.get("Vulnerabilities", []):
            if v["Severity"] not in ["HIGH", "CRITICAL"]:
                continue
            cve = v["VulnerabilityID"]
            assert cve in groups, f"Unreviewed finding {cve}"
            category, note = groups[cve]
            primary = (
                "https://github.com/go-jose/go-jose/security/advisories/GHSA-mgcc-cww5-fp2q"
                if cve == "CVE-2026-116587"
                else vendor[cve]["url"]
            )
            instances.append(
                {
                    "image": name,
                    "target": r["Target"],
                    "cve": cve,
                    "package": v["PkgName"],
                    "version": v["InstalledVersion"],
                    "severity": v["Severity"],
                    "vendor_fixed_version": v.get("FixedVersion") or None,
                    "category": category,
                    "evidence": note,
                    "primary_vendor": primary,
                    "scan_report": report.as_posix(),
                    "disposition": "PENDING HUMAN SECURITY REVIEW; not accepted",
                }
            )
# Deliberately supplement the Alpine feed. Absence from its report is NOT a fix.
manual = []
for cve in [
    "CVE-2026-74860",
    "CVE-2026-86138",
    "CVE-2026-86139",
    "CVE-2026-86140",
    "CVE-2026-86142",
    "CVE-2026-86143",
    "CVE-2026-86144",
]:
    manual.append(
        {
            "image": "postgres",
            "package": "libxml2",
            "version": "2.13.9-r2",
            "cve": cve,
            "historical_severity": "HIGH",
            "scanner_reported": False,
            "category": "insufficient backport evidence; plausible indirect exposure through SQL/XML"
            if cve != "CVE-2026-74860"
            else "configuration-limited Python SAX binding advisory; exact installed binding path not established",
            "primary_vendor": vendor[cve]["url"],
            "evidence": "Official Alpine installed package is true 2.13.9, not Debian reverted 2.9.14. Alpine secdb does not list this advisory; no proof of a backport to this package was obtained. SQL/XML was positively executed; no application XML columns/arbitrary-SQL HTTP feature. CVE-specific exploitability was not reproduced. Preserve as unresolved, not fixed/not-affected.",
            "disposition": "PENDING HUMAN SECURITY REVIEW; obtain package-vendor backport evidence, wait for supported patch, or explicitly accept a bounded Mode A exception with owner/expiry/monitoring. No acceptance granted.",
        }
    )
out = {
    "raw_high_critical_instances": len(instances),
    "raw_critical_instances": sum(i["severity"] == "CRITICAL" for i in instances),
    "raw_unique_cves": len({i["cve"] for i in instances}),
    "manual_xml_advisories": len(manual),
    "security_gate_passed": False,
    "human_risk_acceptance": False,
    "instances": instances,
    "manual_additional_findings": manual,
    "resolved_critical": {
        "cve": "CVE-2026-6653",
        "old_package": "Debian reverted libxml2 2.9.14",
        "new_package": "Alpine true libxml2 2.13.9-r2",
        "basis": "Vendor identifies fix in upstream 2.11.0; new supported variant is above that version. This does not resolve later libxml2 advisories.",
        "primary_vendor": vendor["CVE-2026-6653"]["url"],
    },
    "historical_evidence_preserved": [
        "docs/evidence/step6",
        "docs/evidence/step6_5",
        "docs/evidence/step6_6/postgres.trivy.json",
    ],
}
(root / "residual-security-dispositions.json").write_text(
    json.dumps(out, indent=2) + "\n"
)
print(
    json.dumps(
        {
            k: v
            for k, v in out.items()
            if k
            not in [
                "instances",
                "manual_additional_findings",
                "resolved_critical",
                "historical_evidence_preserved",
            ]
        }
    )
)
