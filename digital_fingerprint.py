"""Professional digital fingerprint report generator.

This tool is intentionally consent-first:
- It does NOT scrape private social data from phone numbers or emails.
- It only uses information you provide directly.
- It creates a polished, shareable report for due-diligence workflows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SubjectProfile:
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None
    social_profiles: Optional[Dict[str, str]] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    consent_confirmed: bool = False


@dataclass
class FingerprintReport:
    generated_at_utc: str
    subject: SubjectProfile
    profile_completeness_score: int
    consistency_score: int
    trust_tier: str
    findings: List[str]
    recommended_next_steps: List[str]
    profile_fingerprint_sha256: str


def canonical_subject_payload(subject: SubjectProfile) -> str:
    payload = {
        "full_name": (subject.full_name or "").strip().lower(),
        "email": (subject.email or "").strip().lower(),
        "phone": (subject.phone or "").strip(),
        "country": (subject.country or "").strip().lower(),
        "role": (subject.role or "").strip().lower(),
        "organization": (subject.organization or "").strip().lower(),
        "website": (subject.website or "").strip().lower(),
        "social_profiles": {
            (k or "").strip().lower(): (v or "").strip().lower()
            for k, v in sorted((subject.social_profiles or {}).items())
        },
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def completeness_score(subject: SubjectProfile) -> int:
    fields = [
        subject.full_name,
        subject.email,
        subject.phone,
        subject.country,
        subject.role,
        subject.organization,
        subject.website,
    ]
    present = sum(1 for field in fields if field)
    social_bonus = 1 if subject.social_profiles else 0
    return min(100, int(((present + social_bonus) / (len(fields) + 1)) * 100))


def consistency_score(subject: SubjectProfile) -> int:
    score = 50

    if subject.email and "@" in subject.email:
        score += 15
    if subject.phone and len("".join(filter(str.isdigit, subject.phone))) >= 8:
        score += 10
    if subject.website and subject.website.startswith(("http://", "https://")):
        score += 10
    if subject.social_profiles and len(subject.social_profiles) >= 2:
        score += 10
    if subject.organization and subject.role:
        score += 5

    return min(100, score)


def trust_tier(completeness: int, consistency: int) -> str:
    weighted = (0.6 * completeness) + (0.4 * consistency)
    if weighted >= 85:
        return "High Confidence"
    if weighted >= 65:
        return "Medium Confidence"
    return "Needs Verification"


def build_findings(subject: SubjectProfile, completeness: int, consistency: int) -> List[str]:
    findings: List[str] = []

    findings.append(f"Profile completeness score is {completeness}/100.")
    findings.append(f"Data consistency score is {consistency}/100.")

    if not subject.consent_confirmed:
        findings.append("Consent was not confirmed. Report should be considered draft-only.")
    else:
        findings.append("Consent confirmed by operator.")

    if subject.social_profiles:
        findings.append(f"{len(subject.social_profiles)} social profile links were provided directly.")
    else:
        findings.append("No social profile links were provided.")

    if subject.email:
        email_domain = subject.email.split("@")[-1].lower() if "@" in subject.email else "invalid"
        findings.append(f"Email domain observed: {email_domain}.")

    return findings


def next_steps(subject: SubjectProfile, tier: str) -> List[str]:
    steps = [
        "Store this report with an internal reference ID.",
        "Revalidate key fields every 90 days.",
    ]

    if tier != "High Confidence":
        steps.append("Request one additional verified identifier (e.g., official website or business profile).")
    if not subject.social_profiles:
        steps.append("Ask the subject to share public professional profile links for stronger verification.")
    if not subject.consent_confirmed:
        steps.append("Collect and record explicit consent before operational use.")

    return steps


def generate_report(subject: SubjectProfile) -> FingerprintReport:
    completeness = completeness_score(subject)
    consistency = consistency_score(subject)
    tier = trust_tier(completeness, consistency)

    fingerprint = hashlib.sha256(canonical_subject_payload(subject).encode("utf-8")).hexdigest()

    return FingerprintReport(
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        subject=subject,
        profile_completeness_score=completeness,
        consistency_score=consistency,
        trust_tier=tier,
        findings=build_findings(subject, completeness, consistency),
        recommended_next_steps=next_steps(subject, tier),
        profile_fingerprint_sha256=fingerprint,
    )


def load_subject(path: Path) -> SubjectProfile:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SubjectProfile(
        full_name=data.get("full_name", "").strip(),
        email=data.get("email"),
        phone=data.get("phone"),
        country=data.get("country"),
        role=data.get("role"),
        organization=data.get("organization"),
        social_profiles=data.get("social_profiles") or {},
        website=data.get("website"),
        notes=data.get("notes"),
        consent_confirmed=bool(data.get("consent_confirmed", False)),
    )


def report_to_markdown(report: FingerprintReport) -> str:
    social_lines = "\n".join(
        [f"- **{platform}**: {url}" for platform, url in (report.subject.social_profiles or {}).items()]
    ) or "- None provided"

    findings = "\n".join([f"- {item}" for item in report.findings])
    steps = "\n".join([f"- {item}" for item in report.recommended_next_steps])

    return f"""# Digital Fingerprint Report

Generated: {report.generated_at_utc}

## Subject
- **Name**: {report.subject.full_name}
- **Role**: {report.subject.role or 'N/A'}
- **Organization**: {report.subject.organization or 'N/A'}
- **Country**: {report.subject.country or 'N/A'}
- **Email**: {report.subject.email or 'N/A'}
- **Phone**: {report.subject.phone or 'N/A'}
- **Website**: {report.subject.website or 'N/A'}

## Public Profiles (provided by subject/operator)
{social_lines}

## Professional Assessment
- **Profile Completeness**: {report.profile_completeness_score}/100
- **Consistency Score**: {report.consistency_score}/100
- **Trust Tier**: {report.trust_tier}
- **Consent Confirmed**: {'Yes' if report.subject.consent_confirmed else 'No'}

## Findings
{findings}

## Recommended Next Steps
{steps}

## Integrity Fingerprint
`{report.profile_fingerprint_sha256}`
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a consent-first professional digital fingerprint report from provided data."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file with subject details.")
    parser.add_argument("--json-out", default="fingerprint_report.json", help="Path to JSON output report.")
    parser.add_argument("--md-out", default="fingerprint_report.md", help="Path to Markdown output report.")

    args = parser.parse_args()

    subject = load_subject(Path(args.input))
    if not subject.full_name:
        raise ValueError("Input JSON must include a non-empty 'full_name'.")

    report = generate_report(subject)

    Path(args.json_out).write_text(
        json.dumps(
            {
                **asdict(report),
                "subject": asdict(report.subject),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    Path(args.md_out).write_text(report_to_markdown(report), encoding="utf-8")

    print(f"Report written to {args.json_out} and {args.md_out}")


if __name__ == "__main__":
    main()
