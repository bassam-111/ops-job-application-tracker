"""Command-line interface for the Ops Job Application Tracker.

Usage:
    python3 cli.py list [--status Applied]
    python3 cli.py summary
    python3 cli.py due [--days 7]
    python3 cli.py followups
    python3 cli.py add --company X --role Y --location Remote --work-mode Remote \
        --status Applied --applied-date 2026-10-28
"""
import argparse
from datetime import date
from pathlib import Path

from tracker import (
    add_application, due_soon, follow_ups_due, load_applications,
    overdue_deadlines, save_applications, summary,
)

DEFAULT_CSV = Path(__file__).with_name("applications.csv")


def _print_row(row):
    deadline = row["deadline"] or "-"
    follow_up = row["follow_up_date"] or "-"
    print(f"{row['company']} | {row['role']} | {row['location']} "
          f"({row['work_mode']}) | {row['status']} | "
          f"applied {row['applied_date']} | deadline {deadline} | "
          f"follow-up {follow_up}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ops Job Application Tracker")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="CSV file to use")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List applications")
    p_list.add_argument("--status", default=None)

    sub.add_parser("summary", help="Show totals by status")

    p_due = sub.add_parser("due", help="Deadlines due soon (and overdue)")
    p_due.add_argument("--days", type=int, default=7)

    sub.add_parser("followups", help="Follow-ups due today or earlier")

    p_add = sub.add_parser("add", help="Add an application")
    for field in ("company", "role", "location", "work_mode", "status",
                  "applied_date", "deadline", "follow_up_date",
                  "contact_email", "notes"):
        p_add.add_argument(f"--{field.replace('_', '-')}",
                           default="" if field not in ("company", "role") else None,
                           required=field in ("company", "role"))

    args = parser.parse_args(argv)
    rows = load_applications(args.csv)
    today = date.today()

    if args.command == "list":
        shown = [r for r in rows if args.status is None or r["status"] == args.status]
        for row in shown:
            _print_row(row)
        print(f"{len(shown)} application(s)")
    elif args.command == "summary":
        result = summary(rows)
        print(f"Total: {result['total']}")
        for status, count in sorted(result["by_status"].items()):
            print(f"  {status}: {count}")
    elif args.command == "due":
        for row in overdue_deadlines(rows, today):
            print(f"OVERDUE: ", end="")
            _print_row(row)
        for row in due_soon(rows, args.days, today):
            print("DUE SOON: ", end="")
            _print_row(row)
    elif args.command == "followups":
        for row in follow_ups_due(rows, today):
            _print_row(row)
        if not follow_ups_due(rows, today):
            print("No follow-ups due.")
    elif args.command == "add":
        row = add_application(rows, **{f: getattr(args, f) for f in (
            "company", "role", "location", "work_mode", "status",
            "applied_date", "deadline", "follow_up_date",
            "contact_email", "notes")})
        save_applications(args.csv, rows)
        print("Added:")
        _print_row(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
