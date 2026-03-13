from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st

from digital_fingerprint import ActivitySignal, SubjectProfile, generate_report, report_to_markdown

st.set_page_config(page_title="Digital Fingerprint Command Center", page_icon="🛰️", layout="wide")

st.markdown(
    """
    <style>
      .stApp {background: radial-gradient(circle at top, #0b1220 0%, #05070f 50%, #020305 100%); color: #d7e3ff;}
      .title-block {padding: 16px 20px; border: 1px solid #1d355d; border-radius: 10px; background: rgba(6,15,30,.65);}
      .small-note {font-size: .85rem; color: #94a7c6;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="title-block"><h2>🛰️ Digital Fingerprint Command Center</h2><p class="small-note">Input can be email or phone only. Add social endpoints and signals for stronger confidence.</p></div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1])

with left:
    st.subheader("Primary Identifiers")
    email = st.text_input("Email", value="jordan.blake@northbridge.co")
    phone = st.text_input("Phone", value="+1-415-555-0138")
    full_name = st.text_input("Full name (optional)", value="")

    st.subheader("Profile Details")
    country = st.text_input("Country", value="US")
    role = st.text_input("Role", value="Business Development Manager")
    organization = st.text_input("Organization", value="Northbridge Advisory")
    website = st.text_input("Website", value="https://northbridge.co")
    aliases = st.text_input("Known aliases (comma-separated)", value="J. Blake")
    consent_confirmed = st.checkbox("Consent confirmed", value=True)

with right:
    st.subheader("Social Media / API Endpoints")
    linkedin = st.text_input("LinkedIn URL", value="https://www.linkedin.com/in/jordanblake")
    x_url = st.text_input("X/Twitter URL", value="https://x.com/jordanblake")
    github = st.text_input("GitHub URL", value="https://github.com/jordanblake")
    facebook = st.text_input("Facebook URL", value="")
    instagram = st.text_input("Instagram URL", value="")
    youtube = st.text_input("YouTube URL", value="")
    tiktok = st.text_input("TikTok URL", value="")
    telegram = st.text_input("Telegram URL", value="")
    reddit = st.text_input("Reddit URL", value="")

st.subheader("Activity Signals")
default_signal_table = pd.DataFrame(
    [
        {
            "source": "LinkedIn API",
            "category": "professional_presence",
            "confidence": 92,
            "timestamp_utc": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "details": "Profile active with recent updates",
        },
        {
            "source": "Company Website",
            "category": "organizational_affiliation",
            "confidence": 88,
            "timestamp_utc": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "details": "Leadership page references subject",
        },
    ]
)
edited_signals = st.data_editor(default_signal_table, num_rows="dynamic", use_container_width=True)


def parse_activity_signals(rows: List[Dict[str, Any]]) -> List[ActivitySignal]:
    parsed: List[ActivitySignal] = []
    for index, row in enumerate(rows, start=1):
        source = str(row.get("source", "")).strip()
        category = str(row.get("category", "")).strip()
        timestamp_utc = str(row.get("timestamp_utc", "")).strip()
        details = str(row.get("details", "")).strip()
        try:
            confidence = int(row.get("confidence", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Signal row {index}: confidence must be an integer.") from exc

        if not source or not category or not timestamp_utc:
            raise ValueError(f"Signal row {index}: source, category, and timestamp_utc are required.")
        if not 0 <= confidence <= 100:
            raise ValueError(f"Signal row {index}: confidence must be between 0 and 100.")

        parsed.append(ActivitySignal(source=source, category=category, confidence=confidence, timestamp_utc=timestamp_utc, details=details))
    return parsed


if st.button("Generate Professional Report", type="primary"):
    if not email.strip() and not phone.strip():
        st.error("Provide at least one primary identifier: email or phone.")
        st.stop()

    social_profiles = {
        "LinkedIn": linkedin,
        "X": x_url,
        "GitHub": github,
        "Facebook": facebook,
        "Instagram": instagram,
        "YouTube": youtube,
        "TikTok": tiktok,
        "Telegram": telegram,
        "Reddit": reddit,
    }
    social_profiles = {k: v.strip() for k, v in social_profiles.items() if v.strip()}

    try:
        activity_signals = parse_activity_signals(edited_signals.to_dict(orient="records"))
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    subject = SubjectProfile(
        full_name=full_name.strip(),
        email=email.strip() or None,
        phone=phone.strip() or None,
        country=country.strip() or None,
        role=role.strip() or None,
        organization=organization.strip() or None,
        social_profiles=social_profiles,
        website=website.strip() or None,
        known_aliases=[item.strip() for item in aliases.split(",") if item.strip()],
        activity_signals=activity_signals,
        consent_confirmed=consent_confirmed,
    )

    report = generate_report(subject)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Completeness", f"{report.profile_completeness_score}/100")
    m2.metric("Consistency", f"{report.consistency_score}/100")
    m3.metric("Signal Strength", f"{report.signal_strength_score}/100")
    m4.metric("Operational Risk", f"{report.operational_risk_score}/100")

    st.markdown(f"### Trust Tier: `{report.trust_tier}`")

    risk_df = pd.DataFrame(
        {
            "dimension": ["Completeness", "Consistency", "Signal Strength", "Operational Risk"],
            "score": [
                report.profile_completeness_score,
                report.consistency_score,
                report.signal_strength_score,
                report.operational_risk_score,
            ],
        }
    )
    fig = px.bar(risk_df, x="dimension", y="score", color="dimension", height=380)
    fig.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Findings")
    for item in report.findings:
        st.write(f"- {item}")

    st.subheader("Recommended Actions")
    for item in report.recommended_next_steps:
        st.write(f"- {item}")

    report_json = json.dumps(asdict(report), indent=2)
    report_md = report_to_markdown(report)

    st.download_button("Download JSON report", report_json, file_name="fingerprint_report.json", mime="application/json")
    st.download_button("Download Markdown report", report_md, file_name="fingerprint_report.md", mime="text/markdown")

st.caption("Built for lawful workflows with provided/authorized data. No hidden scraping is performed.")
