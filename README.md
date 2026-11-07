# Ops Job Application Tracker

A small, honest tool for keeping a job search organised: track applications,
their deadlines, and when to follow up — from one plain CSV file, with a
command-line view and a simple web dashboard.

Built by Bassam Zafar, Operations Executive (Islamabad, BS in AI), as a
portfolio project. No accounts, no tracking, no external services — your data
stays in your own CSV file.

## What it does

- **List** applications, optionally filtered by status
- **Summary** — total applications and a count per status
- **Due** — overdue deadlines plus deadlines due in the next 7 days (default)
- **Follow-ups** — applications whose follow-up date is today or past
- **Add** — append a new application to the CSV
- **Web view** — a local dashboard at `http://127.0.0.1:8000` with status
  filters and OVERDUE / DUE SOON / FOLLOW-UP DUE flags

## Run it

Python 3.10+ only, no packages to install:

```bash
python3 cli.py summary
python3 cli.py list
python3 cli.py list --status Applied
python3 cli.py due --days 7
python3 cli.py followups
python3 cli.py add --company "Example Corp" --role "Operations Coordinator" \
  --location Remote --work-mode Remote --status Applied \
  --applied-date 2026-10-28 --follow-up-date 2026-11-04
python3 web.py   # then open http://127.0.0.1:8000
```

## Data

Edit `applications.csv` directly, or use `cli.py add`. Columns:

`company, role, location, work_mode, status, applied_date, deadline,
follow_up_date, contact_email, notes`

Dates are `YYYY-MM-DD`. Blank deadlines and follow-up dates are allowed.
The shipped CSV contains **sample data only** (example.com contacts) — replace
it with your own applications.
All sample records in this repository are fictional.

## Tests

```bash
python3 test_tracker.py
```

Covers status summaries, overdue/due-soon/follow-up logic (including that
closed applications — Rejected/Offer — are not flagged), CSV round-tripping,
adding a row, page rendering, and a live web-server response check.

## Files

| File | Purpose |
| --- | --- |
| `tracker.py` | Core logic: load/save CSV, summaries, due-date rules |
| `cli.py` | Command-line interface |
| `web.py` | Standard-library web dashboard |
| `test_tracker.py` | Tests (unittest) |
| `applications.csv` | Sample data |
| `requirements.txt` | No external dependencies |

## Notes

This project does not claim any certification, course completion, or
employment outcome. It is a practical tool built from real job-search needs:
deadlines slip, follow-ups get forgotten, and a single CSV plus a quick
dashboard keeps both visible.
