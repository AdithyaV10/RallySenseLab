"""Compare immutable scan evidence without suppressing findings or approving residual risk."""

import json
from collections import Counter
from pathlib import Path

root = Path("docs/evidence/step6_5")
final = {
    "api": "final/api",
    "api_readonly": "final/api_readonly",
    "web": "final/web",
    "postgres": "final/postgres",
    "caddy": "caddy",
}
old_triage = json.loads(
    Path("docs/evidence/step6/vulnerability-triage.json").read_text()
)
known = {(r["image"], r["package"], r["id"]): r for r in old_triage["instances"]}
vendor = json.loads((root / "residual-debian-vendor-evidence.json").read_text())
comparisons, residual = [], []
for name, report_name in final.items():
    before_name = "api" if name == "api_readonly" else name
    before = json.loads(
        Path(f"docs/evidence/step6/{before_name}.trivy.json").read_text()
    )
    after = json.loads((root / f"{report_name}.trivy.json").read_text())

    def findings(report):
        return [
            dict(v, target=t["Target"], package_class=t.get("Class"))
            for t in report["Results"]
            for v in t.get("Vulnerabilities", [])
            if v["Severity"] in {"HIGH", "CRITICAL"}
        ]

    b, a = findings(before), findings(after)
    before_scan = json.loads(
        Path(f"docs/evidence/step6/{before_name}.scan-command.json").read_text()
    )
    after_scan = json.loads((root / f"{report_name}.scan-command.json").read_text())
    ids_before, ids_after = (
        {v["VulnerabilityID"] for v in b},
        {v["VulnerabilityID"] for v in a},
    )
    comparisons.append(
        {
            "image": name,
            "before_identity": {
                k: before_scan[k]
                for k in ["image_id", "archive_sha256", "archive_bytes"]
            },
            "after_identity": {
                k: after_scan[k]
                for k in ["image_id", "archive_sha256", "archive_bytes"]
            },
            "before_report": f"docs/evidence/step6/{before_name}.trivy.json",
            "after_report": f"docs/evidence/step6_5/{report_name}.trivy.json",
            "before": {
                "counts": dict(Counter(v["Severity"] for v in b)),
                "distinct_advisories": len(ids_before),
                "fix_listed_instances": sum(bool(v.get("FixedVersion")) for v in b),
            },
            "after": {
                "counts": dict(Counter(v["Severity"] for v in a)),
                "distinct_advisories": len(ids_after),
                "fix_listed_instances": sum(bool(v.get("FixedVersion")) for v in a),
            },
            "no_longer_reported_advisories": sorted(ids_before - ids_after),
            "newly_reported_advisories": sorted(ids_after - ids_before),
            "coverage_note": "Custom FFmpeg is not an OS-managed component: consult native component inventory and advisory matrix; absence from scanner alone is not remediation evidence.",
        }
    )
    for item in a:
        vid, package = item["VulnerabilityID"], item["PkgName"]
        prior = (
            known.get((before_name, package, vid))
            or known.get(("api", package, vid))
            or known.get(("postgres", package, vid), {})
        )
        group = prior.get("review_group", "NEW_VENDOR_REVIEW_REQUIRED")
        statement = prior.get(
            "disposition",
            "New residual finding requires explicit vendor/applicability review",
        )
        if package == "libxml2":
            group = "PRIVATE_POSTGRES_XML_REQUIRES_HUMAN_DECISION"
            statement = "Genuinely affected stable vendor library; no safe compatible stable fix available. API/worker images no longer include it. PostgreSQL retains SQL/XML capability; application provides no arbitrary SQL/XML interface and uses parameterized SQLAlchemy. This is reduced app exposure, not a claim that the library or authenticated SQL users are unaffected."
        elif vid == "CVE-2026-116587":
            group = "GATEWAY_JWK_CONFIG_SCOPED_REVIEW"
            statement = "Upstream v3 has no patch. The reviewed gateway only reverse-proxies, has admin disabled and exposes no acme_server/JWK/JWT endpoint. Parsing untrusted private RSA JWK is required by the advisory. Configuration-scoped applicability proposal only; any PKI/admin/JWK feature change invalidates it."
        elif vid == "CVE-2023-45853":
            statement = "Exact bookworm zlib source match: Debian says affected contrib/minizip is not built. Final supported trixie image is intended to remove this match; retain if scanner still reports it."
        elif vid == "CVE-2026-76844":
            statement = "Debian confirms a real zlib gz_write buffer-pointer defect despite misleading scanner title. Do not dismiss based on title. Supported trixie security package patches it; any residual instance still requires review."
        elif vid == "CVE-2025-69720":
            statement = "Vendor identifies infocmp CLI analyze_string; no app invokes infocmp or consumes terminal capability data from uploads. Source-wide libtinfo/ncurses binary matches do not establish vulnerable infocmp code in each library. No broad suppression approved."
        references = (
            [vendor[vid]["url"]]
            if vid in vendor
            else [
                u
                for u in item.get("References", [])
                if any(d in u for d in ["github.com", "go.dev", "python.org"])
            ]
        )
        residual.append(
            {
                "image": name,
                "target": item["target"],
                "advisory": vid,
                "package": package,
                "installed_version": item["InstalledVersion"],
                "fixed_version": item.get("FixedVersion"),
                "severity": item["Severity"],
                "title": item.get("Title"),
                "review_group": group,
                "assessment": statement,
                "vendor_evidence": references,
                "status": "human_review_required",
                "human_security_approval": False,
            }
        )
output = {
    "scanner_security_gate_passed": False,
    "human_approval_granted": False,
    "comparisons": comparisons,
    "residual_instances": residual,
}
(root / "before-after-security.json").write_text(
    json.dumps(output, indent=2), encoding="utf-8"
)
print(json.dumps(comparisons, indent=2))
