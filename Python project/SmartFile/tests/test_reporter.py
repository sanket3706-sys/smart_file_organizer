"""
Unit Tests for SmartFile Reporter Module
Tests inventory CSV creation, TXT report generation, and organization history logging.
"""

import os
import sys
import tempfile
import unittest
import csv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from reporter import save_inventory_and_report, save_history, get_recent_history, INVENTORY_FILE, REPORT_FILE

class TestReporter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.files = [
            {"filename": "DSA_assignment.txt", "ext": ".txt", "size": 1024, "path": "/path/DSA_assignment.txt"},
            {"filename": "Physics_lab.txt", "ext": ".txt", "size": 2048, "path": "/path/Physics_lab.txt"}
        ]
        self.analysis_data = {
            "total_files": 2,
            "total_size_bytes": 3072,
            "total_size_mb": 3072 / (1024 * 1024),
            "ext_counts": {".TXT": 2},
            "largest_file": self.files[1],
            "smallest_file": self.files[0]
        }

    def tearDown(self):
        self.test_dir.cleanup()

    def test_save_inventory_and_report(self):
        """Verify that inventory.csv and file_report.txt are created and formatted properly."""
        success = save_inventory_and_report(self.test_dir.name, self.files, self.analysis_data)
        self.assertTrue(success)

        # Check inventory file exists and is populated
        self.assertTrue(os.path.exists(INVENTORY_FILE))
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["filename"], "DSA_assignment.txt")

        # Check text report exists and contains expected sections
        self.assertTrue(os.path.exists(REPORT_FILE))
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("SMARTFILE INVENTORY & AUDIT REPORT", content)
            self.assertIn("FILE TYPE DISTRIBUTION", content)
            self.assertIn("DSA_assignment.txt", content)

    def test_save_and_retrieve_history(self):
        """Verify that file operations are logged into organization_history.csv."""
        save_history("Moved", "/source/test.txt", "/dest/test.txt")
        recent = get_recent_history(5)
        self.assertGreaterEqual(len(recent), 1)
        last_entry = recent[-1]
        self.assertEqual(last_entry[2], "Moved")
        self.assertEqual(last_entry[3], "/source/test.txt")
        self.assertEqual(last_entry[4], "/dest/test.txt")

if __name__ == "__main__":
    unittest.main()
