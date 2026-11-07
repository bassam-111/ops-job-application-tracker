"""Core logic for the Ops Job Application Tracker.

No external dependencies: reads/writes a plain CSV so the tracker stays
portable and easy to inspect. Dates are ISO format (YYYY-MM-DD).
"""
import csv
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

FIELDS = [
    "company", "role", "location", "work_mode", "status",
    "applied_date", "deadline", "follow_up_date", "contact_email", "notes",
]


def parse_date(value):
    """Return a date or None for a blank/invalid value."""
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def load_applications(path):
    """Load applications from CSV into a list of dicts."""
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_applications(path, rows):
    """Write applications back to CSV, preserving the column order."""
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def add_application(rows, **kwargs):
    """Append one application row (unknown keys are ignored)."""
    row = {k: kwargs.get(k, "") for k in FIELDS}
    rows.append(row)
    return row


def summary(rows):
    """Return total count and a per-status breakdown."""
    return {"total": len(rows), "by_status": dict(Counter(r["status"] for r in rows))}


def overdue_deadlines(rows, today=None):
    """Applications whose deadline passed and are not closed (Rejected/Offer)."""
    today = today or date.today()
    closed = {"Rejected", "Offer"}
    out = []
    for row in rows:
        deadline = parse_date(row.get("deadline", ""))
        if deadline and deadline < today and row["status"] not in closed:
            out.append(row)
    return out


def due_soon(rows, days=7, today=None):
    """Open applications with a deadline within the next `days` days."""
    today = today or date.today()
    horizon = today + timedelta(days=days)
    closed = {"Rejected", "Offer"}
    out = []
    for row in rows:
        deadline = parse_date(row.get("deadline", ""))
        if deadline and today <= deadline <= horizon and row["status"] not in closed:
            out.append(row)
    return sorted(out, key=lambda r: r["deadline"])


def follow_ups_due(rows, today=None):
    """Open applications whose follow-up date is today or past."""
    today = today or date.today()
    closed = {"Rejected", "Offer"}
    out = []
    for row in rows:
        follow_up = parse_date(row.get("follow_up_date", ""))
        if follow_up and follow_up <= today and row["status"] not in closed:
            out.append(row)
    return sorted(out, key=lambda r: r["follow_up_date"])
