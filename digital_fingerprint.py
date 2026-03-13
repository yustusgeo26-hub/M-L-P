"""Professional digital fingerprint intelligence report generator.

Consent-first by design:
- No scraping from phone numbers/emails.
- No hidden collection.
- Only analyzes data explicitly supplied by an authorized operator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional


@dataclass
class ActivitySignal:
    source: str
    category: str
    confidence: int
    timestamp_utc: str
    details: str = ""


@dataclass
class SubjectProfile:
    full_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None
    social_profiles: Optional[Dict[str, str]] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    known_aliases: Optional[List[str]] = None
    activity_signals: Optional[List[ActivitySignal]] = None
    consent_confirmed: bool = False


@dataclass
class FingerprintReport:
    generated_at_utc: str
    subject: SubjectProfile
    profile_completeness_score: int
    consistency_score: int
    signal_strength_score: int
    operational_risk_score: int
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
        "known_aliases": [alias.strip().lower() for alias in (subject.known_aliases or [])],
        "social_profiles": {
            (k or "").strip().lower(): (v or "").strip().lower()
            for k, v in sorted((subject.social_profiles or {}).items())
        },
        "activity_signals": [
            {
                "source": signal.source.strip().lower(),
                "category": signal.category.strip().lower(),
                "confidence": signal.confidence,
                "timestamp_utc": signal.timestamp_utc,
                "details": signal.details.strip().lower(),
            }
            for signal in sorted(
                (subject.activity_signals or []), key=lambda item: (item.timestamp_utc, item.source)
            )
        ],
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
    signal_bonus = 1 if subject.activity_signals else 0
    alias_bonus = 1 if subject.known_aliases else 0
    return min(100, int(((present + social_bonus + signal_bonus + alias_bonus) / (len(fields) + 3)) * 100))


def consistency_score(subject: SubjectProfile) -> int:
    score = 45

    if subject.email and "@" in subject.email and "." in subject.email.split("@")[-1]:
        score += 15
    if subject.phone and len("".join(filter(str.isdigit, subject.phone))) >= 8:
        score += 10
    if subject.website and subject.website.startswith(("http://", "https://")):
        score += 10
    if subject.social_profiles and len(subject.social_profiles) >= 2:
        score += 10
    if subject.organization and subject.role:
        score += 5
    if subject.activity_signals and all(0 <= signal.confidence <= 100 for signal in subject.activity_signals):
        score += 5

    return min(100, score)


def signal_strength_score(subject: SubjectProfile) -> int:
    if not subject.activity_signals:
        return 0

    average_confidence = int(mean(signal.confidence for signal in subject.activity_signals))
    variety_bonus = min(20, len({signal.category.lower() for signal in subject.activity_signals}) * 5)
    recency_bonus = 10

    return min(100, average_confidence + variety_bonus + recency_bonus)


def operational_risk_score(subject: SubjectProfile, consistency: int, signal_strength: int) -> int:
    risk = 60

    if subject.consent_confirmed:
        risk -= 15
    if consistency >= 80:
        risk -= 10
    if signal_strength >= 70:
        risk -= 10
    if not subject.social_profiles:
        risk += 5
    if not subject.website:
        risk += 5

    return max(0, min(100, risk))


def trust_tier(completeness: int, consistency: int, signal_strength: int, risk: int) -> str:
    weighted = (0.35 * completeness) + (0.30 * consistency) + (0.20 * signal_strength) + (0.15 * (100 - risk))
    if weighted >= 82:
        return "Tier-1 / High Confidence"
    if weighted >= 65:
        return "Tier-2 / Moderate Confidence"
    return "Tier-3 / Requires Manual Verification"


def build_findings(subject: SubjectProfile, completeness: int, consistency: int, signal_strength: int, risk: int) -> List[str]:
    findings = [
        f"Profile completeness score: {completeness}/100.",
        f"Data consistency score: {consistency}/100.",
        f"Signal strength score: {signal_strength}/100.",
        f"Operational risk score: {risk}/100.",
    ]

    findings.append("Consent status: confirmed." if subject.consent_confirmed else "Consent status: missing.")

    if subject.social_profiles:
        findings.append(f"Provided social endpoints: {len(subject.social_profiles)}.")
    if subject.activity_signals:
        findings.append(f"Activity signals evaluated: {len(subject.activity_signals)}.")
    if subject.email:
        domain = subject.email.split("@")[-1].lower() if "@" in subject.email else "invalid"
        findings.append(f"Observed email domain: {domain}.")

    return findings


def next_steps(subject: SubjectProfile, tier: str, risk: int) -> List[str]:
    steps = [
        "Attach this report to a case ID and evidence owner.",
        "Schedule periodic refresh of supplied identifiers.",
    ]

    if risk >= 50:
        steps.append("Escalate to analyst review before operational decisions.")
    if "Tier-3" in tier:
        steps.append("Request two additional independent data points from subject.")
    if not subject.consent_confirmed:
        steps.append("Collect explicit written consent and retention approval.")

    return steps


def generate_report(subject: SubjectProfile) -> FingerprintReport:
    completeness = completeness_score(subject)
    consistency = consistency_score(subject)
    signal_strength = signal_strength_score(subject)
    risk = operational_risk_score(subject, consistency, signal_strength)
    tier = trust_tier(completeness, consistency, signal_strength, risk)

    fingerprint = hashlib.sha256(canonical_subject_payload(subject).encode("utf-8")).hexdigest()

    return FingerprintReport(
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        subject=subject,
        profile_completeness_score=completeness,
        consistency_score=consistency,
        signal_strength_score=signal_strength,
        operational_risk_score=risk,
        trust_tier=tier,
        findings=build_findings(subject, completeness, consistency, signal_strength, risk),
        recommended_next_steps=next_steps(subject, tier, risk),
        profile_fingerprint_sha256=fingerprint,
    )


def load_subject(path: Path) -> SubjectProfile:
    data = json.loads(path.read_text(encoding="utf-8"))
    activity_signals = [ActivitySignal(**item) for item in (data.get("activity_signals") or [])]
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
        known_aliases=data.get("known_aliases") or [],
        activity_signals=activity_signals,
        consent_confirmed=bool(data.get("consent_confirmed", False)),
    )


def report_to_markdown(report: FingerprintReport) -> str:
    social_lines = "\n".join(
        [f"- **{platform}**: {url}" for platform, url in (report.subject.social_profiles or {}).items()]
    ) or "- None provided"
    signal_lines = "\n".join(
        [
            f"- `{s.timestamp_utc}` | **{s.source}** | {s.category} | confidence={s.confidence} | {s.details or 'n/a'}"
            for s in (report.subject.activity_signals or [])
        ]
    ) or "- No activity signals supplied"
    findings = "\n".join([f"- {item}" for item in report.findings])
    steps = "\n".join([f"- {item}" for item in report.recommended_next_steps])

    return f"""# Digital Fingerprint Intelligence Report

Generated: {report.generated_at_utc}

## Subject Identity
- **Name**: {report.subject.full_name or "N/A"}
- **Role**: {report.subject.role or 'N/A'}
- **Organization**: {report.subject.organization or 'N/A'}
- **Country**: {report.subject.country or 'N/A'}
- **Email**: {report.subject.email or 'N/A'}
- **Phone**: {report.subject.phone or 'N/A'}
- **Website**: {report.subject.website or 'N/A'}

## Public Endpoints (operator supplied)
{social_lines}

## Activity Signals
{signal_lines}

## Assessment Matrix
- **Profile Completeness**: {report.profile_completeness_score}/100
- **Consistency Score**: {report.consistency_score}/100
- **Signal Strength**: {report.signal_strength_score}/100
- **Operational Risk**: {report.operational_risk_score}/100
- **Trust Tier**: {report.trust_tier}
- **Consent Confirmed**: {'Yes' if report.subject.consent_confirmed else 'No'}

## Findings
{findings}

## Recommended Actions
{steps}

## Integrity Fingerprint
`{report.profile_fingerprint_sha256}`
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an intelligence-style digital fingerprint report from supplied data.")
    parser.add_argument("--input", required=True, help="Path to input JSON file with subject details.")
    parser.add_argument("--json-out", default="fingerprint_report.json", help="Path to JSON output report.")
    parser.add_argument("--md-out", default="fingerprint_report.md", help="Path to Markdown output report.")

    args = parser.parse_args()

    subject = load_subject(Path(args.input))
    if not subject.email and not subject.phone and not subject.full_name:
        raise ValueError("Input JSON must include at least one identifier: full_name, email, or phone.")

    report = generate_report(subject)

    Path(args.json_out).write_text(
        json.dumps({**asdict(report), "subject": asdict(report.subject)}, indent=2),
        encoding="utf-8",
    )
    Path(args.md_out).write_text(report_to_markdown(report), encoding="utf-8")

    print(f"Report written to {args.json_out} and {args.md_out}")


if __name__ == "__main__":
    main()
