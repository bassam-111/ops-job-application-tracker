"""Tests for tracker.py and the web view. Run: python3 test_tracker.py"""
import tempfile
import threading
import unittest
import urllib.request
from datetime import date
from pathlib import Path

from tracker import (
    add_application, due_soon, follow_ups_due, load_applications,
    overdue_deadlines, save_applications, summary,
)
from web import Handler, render_page
from http.server import ThreadingHTTPServer

ROWS = [
    {"company": "A", "role": "Ops", "location": "Remote", "work_mode": "Remote",
     "status": "Applied", "applied_date": "2026-10-20", "deadline": "2026-10-29",
     "follow_up_date": "2026-10-27", "contact_email": "", "notes": ""},
    {"company": "B", "role": "PM", "location": "Remote", "work_mode": "Remote",
     "status": "Applied", "applied_date": "2026-10-20", "deadline": "2026-10-25",
     "follow_up_date": "", "contact_email": "", "notes": ""},
    {"company": "C", "role": "Data", "location": "Remote", "work_mode": "Remote",
     "status": "Rejected", "applied_date": "2026-10-10", "deadline": "2026-10-12",
     "follow_up_date": "", "contact_email": "", "notes": ""},
]

TODAY = date(2026, 10, 28)


class TestTracker(unittest.TestCase):
    def test_summary(self):
        result = summary(ROWS)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["by_status"]["Applied"], 2)
        self.assertEqual(result["by_status"]["Rejected"], 1)

    def test_overdue_excludes_closed(self):
        # B is overdue, C is past deadline but Rejected so excluded.
        self.assertEqual([r["company"] for r in overdue_deadlines(ROWS, TODAY)], ["B"])

    def test_due_soon(self):
        self.assertEqual([r["company"] for r in due_soon(ROWS, 7, TODAY)], ["A"])

    def test_follow_ups_due(self):
        self.assertEqual([r["company"] for r in follow_ups_due(ROWS, TODAY)], ["A"])

    def test_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "apps.csv"
            save_applications(path, ROWS)
            loaded = load_applications(path)
            self.assertEqual(len(loaded), 3)
            self.assertEqual(loaded[0]["company"], "A")

    def test_add(self):
        rows = list(ROWS)
        add_application(rows, company="D", role="Ops", status="Applied")
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[-1]["company"], "D")

    def test_render_page_contains_rows(self):
        page = render_page(ROWS)
        self.assertIn("Ops Job Application Tracker", page)
        self.assertIn("OVERDUE", page)
        self.assertIn("FOLLOW-UP DUE", page)

    def test_web_server_responds_200(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urllib.request.urlopen(
                    f"http://127.0.0.1:{server.server_port}/") as resp:
                self.assertEqual(resp.status, 200)
                self.assertIn(b"Ops Job Application Tracker", resp.read())
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
