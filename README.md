# Digital Fingerprint Intelligence Suite

A practical, production-oriented project that generates professional digital fingerprint reports from **authorized, supplied data**.

## What changed (error-fix pass)
- Input supports **email or phone only** (full name optional).
- Added more social endpoints (LinkedIn, X, GitHub, Facebook, Instagram, YouTube, TikTok, Telegram, Reddit).
- Improved Streamlit compatibility to avoid common UI parameter issues.
- Added dependency filename aliases: `requirements.txt`, `requirement.txt`, and `requirement.text`.

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> If you accidentally run one of these, they also work:
> - `pip install -r requirement.txt`
> - `pip install -r requirement.text`

## Run dashboard
```bash
streamlit run app.py
```
Open `http://localhost:8501`.

## Run CLI
```bash
python digital_fingerprint.py --input sample_subject.json --json-out fingerprint_report.json --md-out fingerprint_report.md
```

## Input rules
- Minimum required: **email OR phone**.
- Add social endpoints and activity signals for stronger confidence.

## Common errors fixed
- Missing/incorrect requirements filename (`requirement` vs `requirements`) → alias files added.
- Streamlit chart/editor width compatibility issues → standardized to stable parameters.
- Invalid signal rows → explicit validation and readable error messages.

## Important boundaries
This project is for legal/ethical workflows. It does **not** perform hidden scraping from phone/email by itself.
