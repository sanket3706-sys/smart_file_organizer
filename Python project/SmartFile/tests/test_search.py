"""
Unit Tests for SmartFile Search and Filter Module
Tests keyword searching, extension matching, string methods (split, index, isupper),
and size filtering using lambda & filter().
"""

import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from search import search_by_keyword, search_by_extension, filter_by_size

class TestSearch(unittest.TestCase):
    def setUp(self):
        self.files = [
            {"filename": "DSA_assignment.txt", "ext": ".txt", "size": 1024, "path": "/path/DSA_assignment.txt"},
            {"filename": "DSA_notes.txt", "ext": ".txt", "size": 2048, "path": "/path/DSA_notes.txt"},
            {"filename": "DBMS_assignment.pdf", "ext": ".pdf", "size": 512, "path": "/path/DBMS_assignment.pdf"},
            {"filename": "Screenshot.png", "ext": ".png", "size": 4096, "path": "/path/Screenshot.png"},
            {"filename": "notes_without_ext", "ext": "", "size": 256, "path": "/path/notes_without_ext"}
        ]

    def test_search_by_keyword_found(self):
        """Test searching with matching keyword (case-insensitive)."""
        results = search_by_keyword(self.files, "dsa")
        self.assertEqual(len(results), 2)
        names = [f["filename"] for f in results]
        self.assertIn("DSA_assignment.txt", names)
        self.assertIn("DSA_notes.txt", names)

    def test_search_by_keyword_multi_token_split(self):
        """Test searching with multi-word tokens demonstrating .split()."""
        results = search_by_keyword(self.files, "dsa assignment")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "DSA_assignment.txt")

    def test_search_by_keyword_smart_case_isupper(self):
        """Test smart-case search with uppercase acronym query demonstrating .isupper()."""
        results = search_by_keyword(self.files, "DBMS")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "DBMS_assignment.pdf")

    def test_search_by_keyword_not_found(self):
        """Test searching with non-matching keyword returns empty list."""
        results = search_by_keyword(self.files, "quantum_physics")
        self.assertEqual(results, [])

    def test_search_by_extension_with_and_without_dot(self):
        """Test extension search works whether user provides leading dot or not."""
        results_dot = search_by_extension(self.files, ".pdf")
        results_no_dot = search_by_extension(self.files, "pdf")
        self.assertEqual(len(results_dot), 1)
        self.assertEqual(results_dot[0]["filename"], "DBMS_assignment.pdf")
        self.assertEqual(results_dot, results_no_dot)

    def test_filter_by_size_min_max(self):
        """Test size filtering with filter() and lambda."""
        # Files with size >= 1024 bytes
        large = filter_by_size(self.files, min_bytes=1024)
        self.assertEqual(len(large), 3)  # 1024, 2048, 4096

        # Files between 500 and 1500 bytes
        medium = filter_by_size(self.files, min_bytes=500, max_bytes=1500)
        self.assertEqual(len(medium), 2)  # 512 and 1024

if __name__ == "__main__":
    unittest.main()
