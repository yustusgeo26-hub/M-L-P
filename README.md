# Professional Digital Fingerprint Generator

This project now includes a **consent-first** utility to generate a professional digital fingerprint report from data that is directly provided by a subject or authorized operator.

## Important
This tool does **not** scrape private social information from phone numbers or emails.
Use it only in legal/ethical workflows with explicit consent.

## Quick Start

```bash
python digital_fingerprint.py --input sample_subject.json --json-out fingerprint_report.json --md-out fingerprint_report.md
```

## Input Format
Provide a JSON file with fields like:

- `full_name` (required)
- `email`
- `phone`
- `country`
- `role`
- `organization`
- `website`
- `social_profiles` (object map like `{ "LinkedIn": "https://..." }`)
- `consent_confirmed` (`true`/`false`)

## Output
- `fingerprint_report.json`: structured report data.
- `fingerprint_report.md`: polished summary report.
