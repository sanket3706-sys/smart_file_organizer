"""
Unit Tests for SmartFile Duplicate Detector Module
Tests chunked SHA-256 calculation, detection of confirmed content duplicates,
and accurate separation from potential same-size/different-content groups.
"""

import os
import sys
import tempfile
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from duplicate_detector import calculate_sha256, detect_duplicates

class TestDuplicateDetector(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = self.test_dir.name

    def tearDown(self):
        self.test_dir.cleanup()

    def test_calculate_sha256(self):
        """Test that SHA-256 computation returns identical hashes for identical content."""
        file1 = os.path.join(self.base_path, "file1.txt")
        file2 = os.path.join(self.base_path, "file2.txt")
        file3 = os.path.join(self.base_path, "file3.txt")

        content_a = "Identical cryptographic content string for testing."
        content_b = "Different content string."

        with open(file1, "w", encoding="utf-8") as f:
            f.write(content_a)
        with open(file2, "w", encoding="utf-8") as f:
            f.write(content_a)
        with open(file3, "w", encoding="utf-8") as f:
            f.write(content_b)

        hash1 = calculate_sha256(file1)
        hash2 = calculate_sha256(file2)
        hash3 = calculate_sha256(file3)

        self.assertIsNotNone(hash1)
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)

    def test_detect_duplicates_confirmed_does_not_label_group_as_potential(self):
        """
        Verify that detect_duplicates confirms exact SHA-256 duplicates
        and DOES NOT label an entire size group as potential if files within it
        are already confirmed duplicates.
        """
        f_dup1 = os.path.join(self.base_path, "dup1.txt")
        f_dup2 = os.path.join(self.base_path, "dup2.txt")
        f_same_size_diff_content = os.path.join(self.base_path, "same_size.txt")

        # 16-byte strings
        content1 = "1234567890ABCDEF"
        content2 = "1234567890ABCDEF"
        content3 = "FEDCBA0987654321"  # Same size (16 bytes), different content

        with open(f_dup1, "w") as f:
            f.write(content1)
        with open(f_dup2, "w") as f:
            f.write(content2)
        with open(f_same_size_diff_content, "w") as f:
            f.write(content3)

        files = [
            {"filename": "dup1.txt", "path": f_dup1, "size": 16, "ext": ".txt"},
            {"filename": "dup2.txt", "path": f_dup2, "size": 16, "ext": ".txt"},
            {"filename": "same_size.txt", "path": f_same_size_diff_content, "size": 16, "ext": ".txt"}
        ]

        result = detect_duplicates(files)
        confirmed = result["confirmed_groups"]
        potential = result["potential_groups"]

        # Confirmed group should contain dup1.txt and dup2.txt
        self.assertEqual(len(confirmed), 1)
        confirmed_names = {f["filename"] for f in confirmed[0]}
        self.assertEqual(confirmed_names, {"dup1.txt", "dup2.txt"})

        # The size group must NOT be labeled as potential because dup1 and dup2 are confirmed duplicates
        # and same_size.txt is a single file without another same-size collision partner
        self.assertEqual(len(potential), 0)

    def test_detect_duplicates_potential_only(self):
        """
        Verify that files sharing the exact same size but differing contents
        are properly identified as potential duplicates.
        """
        f1 = os.path.join(self.base_path, "diff1.txt")
        f2 = os.path.join(self.base_path, "diff2.txt")

        content1 = "20_bytes_content_AAA"
        content2 = "20_bytes_content_BBB"

        with open(f1, "w") as f:
            f.write(content1)
        with open(f2, "w") as f:
            f.write(content2)

        files = [
            {"filename": "diff1.txt", "path": f1, "size": len(content1), "ext": ".txt"},
            {"filename": "diff2.txt", "path": f2, "size": len(content2), "ext": ".txt"}
        ]

        result = detect_duplicates(files)
        # No confirmed duplicates
        self.assertEqual(len(result["confirmed_groups"]), 0)
        # One potential duplicate group
        self.assertEqual(len(result["potential_groups"]), 1)
        pot_names = {f["filename"] for f in result["potential_groups"][0]}
        self.assertEqual(pot_names, {"diff1.txt", "diff2.txt"})

    def test_no_duplicates_found(self):
        """Verify behavior when no duplicate files exist."""
        f1 = os.path.join(self.base_path, "f1.txt")
        f2 = os.path.join(self.base_path, "f2.txt")

        with open(f1, "w") as f:
            f.write("ABC")
        with open(f2, "w") as f:
            f.write("DEFGHI")

        files = [
            {"filename": "f1.txt", "path": f1, "size": 3, "ext": ".txt"},
            {"filename": "f2.txt", "path": f2, "size": 6, "ext": ".txt"}
        ]

        result = detect_duplicates(files)
        self.assertEqual(len(result["confirmed_groups"]), 0)
        self.assertEqual(len(result["potential_groups"]), 0)

if __name__ == "__main__":
    unittest.main()
