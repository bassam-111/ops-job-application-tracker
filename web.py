"""Simple web view for the Ops Job Application Tracker.

Standard-library only (http.server), so it runs with plain Python 3.
Start with:  python3 web.py            (listens on http://127.0.0.1:8000)
Filter by status with:  http://127.0.0.1:8000/?status=Applied
"""
import html
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from tracker import (
    due_soon, follow_ups_due, load_applications, overdue_deadlines, summary,
)

CSV_PATH = Path(__file__).with_name("applications.csv")


def render_page(rows, status_filter=None):
    """Build the dashboard HTML for the given rows."""
    today = date.today()
    shown = rows if not status_filter else [r for r in rows if r["status"] == status_filter]
    stats = summary(rows)
    overdue = {r["company"] + r["role"] for r in overdue_deadlines(rows, today)}
    due = {r["company"] + r["role"] for r in due_soon(rows, 7, today)}
    follow = {r["company"] + r["role"] for r in follow_ups_due(rows, today)}

    stat_cards = "".join(
        f"<span class='card'>{html.escape(s)}: {c}</span>"
        for s, c in sorted(stats["by_status"].items()))

    table_rows = ""
    for r in shown:
        key = r["company"] + r["role"]
        badges = []
        if key in overdue:
            badges.append("<b class='overdue'>OVERDUE</b>")
        elif key in due:
            badges.append("<b class='due'>DUE SOON</b>")
        if key in follow:
            badges.append("<b class='follow'>FOLLOW-UP DUE</b>")
        cells = "".join(f"<td>{html.escape(r[f] or '-')}</td>" for f in (
            "company", "role", "location", "work_mode", "status",
            "applied_date", "deadline", "follow_up_date"))
        table_rows += f"<tr>{cells}<td>{' '.join(badges)}</td></tr>"

    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>Ops Job Application Tracker</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccc;padding:6px 8px;text-align:left}}
.card{{display:inline-block;background:#eef;margin:2px;padding:4px 10px;border-radius:12px}}
.overdue{{color:#b00}}.due{{color:#a60}}.follow{{color:#06a}}</style></head>
<body><h1>Ops Job Application Tracker</h1>
<p>Total: {stats['total']} &mdash; {stat_cards}</p>
<p>Filter: <a href="/">All</a> | <a href="/?status=Applied">Applied</a> |
<a href="/?status=Interview">Interview</a> | <a href="/?status=Shortlisted">Shortlisted</a></p>
<table><tr><th>Company</th><th>Role</th><th>Location</th><th>Mode</th>
<th>Status</th><th>Applied</th><th>Deadline</th><th>Follow-up</th><th>Flags</th></tr>
{table_rows}</table>
<p>Sample data only &mdash; replace applications.csv with your own applications.</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (http.server naming)
        query = parse_qs(urlparse(self.path).query)
        status_filter = query.get("status", [None])[0]
        body = render_page(load_applications(CSV_PATH), status_filter).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # keep test output clean
        pass


def main(port=8000):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving on http://127.0.0.1:{port}  (Ctrl+C to stop)")
    server.serve_forever()


if __name__ == "__main__":
    main()
