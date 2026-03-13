# Digital Fingerprint Intelligence Suite

A practical, production-oriented project that generates professional digital fingerprint reports from **authorized, supplied data**.

## What changed (based on your request)
- Input can now be **just email or phone number**.
- Dashboard now supports many social endpoints (not only X/GitHub): LinkedIn, X, GitHub, Facebook, Instagram, YouTube, TikTok, Telegram, and Reddit.
- Validation errors were hardened so malformed signal rows fail clearly.

## Features
- Streamlit intelligence dashboard (`app.py`) for analysts.
- CLI report generator (`digital_fingerprint.py`) for automation/pipelines.
- JSON + Markdown report exports.
- Scoring model: completeness, consistency, signal strength, operational risk, and trust tier.

## Project files
- `app.py` → interactive dashboard.
- `digital_fingerprint.py` → core engine + CLI.
- `sample_subject.json` → sample input.
- `requirements.txt` and `requirement.text` → dependency lists.

## 1) Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Run dashboard (recommended)
```bash
streamlit run app.py
```
Then open the local URL shown in terminal (usually `http://localhost:8501`).

## 3) Run via CLI
```bash
python digital_fingerprint.py --input sample_subject.json --json-out fingerprint_report.json --md-out fingerprint_report.md
```

## Input rules
- Minimum required: **email OR phone** (full name optional).
- Add more social endpoints + activity signals to increase report confidence.

## Troubleshooting
- If `streamlit: command not found`, activate your virtual environment first.
- If dependencies fail, run:
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```
- If port `8501` is busy:
  ```bash
  streamlit run app.py --server.port 8502
  ```

## Important boundaries
This project is designed for legal/ethical workflows. It does **not** do hidden scraping or private data extraction from phone/email alone.
