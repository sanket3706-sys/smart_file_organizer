"""
Unit Tests for SmartFile Analyzer Module
Tests file analysis, statistical aggregations, extension distribution,
and extreme file size detections.
"""

import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from analyzer import analyze_folder

class TestAnalyzer(unittest.TestCase):
    def test_analyze_empty_file_list(self):
        """Test analyzing an empty file list returns an empty dict safely."""
        result = analyze_folder([], show_display=False)
        self.assertEqual(result, {})

    def test_analyze_folder_metrics(self):
        """Test calculation of total files, sizes, extensions, and extremes."""
        files = [
            {"filename": "a.pdf", "ext": ".pdf", "size": 1000, "path": "/a.pdf"},
            {"filename": "b.pdf", "ext": ".pdf", "size": 2000, "path": "/b.pdf"},
            {"filename": "c.txt", "ext": ".txt", "size": 500, "path": "/c.txt"},
            {"filename": "d_no_ext", "ext": "", "size": 100, "path": "/d_no_ext"}
        ]

        data = analyze_folder(files, show_display=False)
        self.assertEqual(data["total_files"], 4)
        self.assertEqual(data["total_size_bytes"], 3600)
        self.assertEqual(data["no_ext_count"], 1)
        self.assertEqual(data["most_common_ext"], ".PDF")

        # Verify largest and smallest file
        self.assertEqual(data["largest_file"]["filename"], "b.pdf")
        self.assertEqual(data["smallest_file"]["filename"], "d_no_ext")

        # Verify unique extensions
        self.assertEqual(data["unique_extension_count"], 3)  # .PDF, .TXT, [no extension]

    def test_paired_ext_data_zip(self):
        """Verify that zip() in analyzer correctly pairs sorted extensions with counts."""
        files = [
            {"filename": "doc1.txt", "ext": ".txt", "size": 100, "path": "/doc1.txt"},
            {"filename": "doc2.txt", "ext": ".txt", "size": 100, "path": "/doc2.txt"},
            {"filename": "img.png", "ext": ".png", "size": 500, "path": "/img.png"}
        ]
        data = analyze_folder(files, show_display=False)
        paired = data["paired_ext_data"]
        # Paired should be [('.TXT', 2), ('.PNG', 1)]
        self.assertEqual(paired[0], (".TXT", 2))
        self.assertEqual(paired[1], (".PNG", 1))

if __name__ == "__main__":
    unittest.main()
