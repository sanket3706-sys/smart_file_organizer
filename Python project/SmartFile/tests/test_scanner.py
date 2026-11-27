"""
Unit Tests for SmartFile Scanner and Validation Module
Tests folder validation, Windows reserved filename rules, file info extraction,
directory scanning, and recursive directory size calculation.
"""

import os
import sys
import tempfile
import unittest

# Ensure SmartFile directory is on the import path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from scanner import validate_folder, get_file_info, scan_folder, calculate_directory_size_recursive
from utils import is_valid_filename

class TestScanner(unittest.TestCase):
    def setUp(self):
        # Create an isolated temporary directory for tests
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = self.test_dir.name

    def tearDown(self):
        # Clean up temporary directory
        self.test_dir.cleanup()

    def test_validate_folder_valid(self):
        """Test that an existing directory validates as True."""
        is_valid, msg = validate_folder(self.base_path)
        self.assertTrue(is_valid)
        self.assertEqual(os.path.abspath(msg), os.path.abspath(self.base_path))

    def test_validate_folder_nonexistent(self):
        """Test that a non-existent path is reported as invalid."""
        fake_path = os.path.join(self.base_path, "does_not_exist_folder")
        is_valid, msg = validate_folder(fake_path)
        self.assertFalse(is_valid)
        self.assertIn("does not exist", msg.lower())

    def test_validate_folder_empty_or_file(self):
        """Test empty path and file path passed to validate_folder."""
        is_valid, msg = validate_folder("")
        self.assertFalse(is_valid)

        # Create a file and test that passing a file fails isdir check
        file_path = os.path.join(self.base_path, "sample.txt")
        with open(file_path, "w") as f:
            f.write("hello")
        is_valid, msg = validate_folder(file_path)
        self.assertFalse(is_valid)
        self.assertIn("not a directory", msg.lower())

    def test_is_valid_filename_windows_reserved_names(self):
        """
        Verify that is_valid_filename rejects Windows reserved device names
        both with and without extensions (CON, PRN, AUX, NUL, COM1-9, LPT1-9).
        """
        reserved_examples = [
            "CON", "con", "aux", "NUL", "PRN",
            "COM1", "com9", "lpt1", "LPT9",
            "CON.txt", "aux.pdf", "com1.docx", "nul.dat", "prn.tar.gz"
        ]
        for name in reserved_examples:
            valid, err = is_valid_filename(name)
            self.assertFalse(valid, f"Expected '{name}' to be rejected as Windows reserved name.")
            self.assertIn("reserved", err.lower())

    def test_is_valid_filename_trailing_dots_and_spaces(self):
        """Verify that filenames ending with a dot or trailing space are rejected."""
        invalid_trailing = ["filename.", "report. ", "notes...", "test "]
        for name in invalid_trailing:
            valid, err = is_valid_filename(name)
            self.assertFalse(valid, f"Expected '{name}' to be rejected due to trailing dot/space.")

    def test_is_valid_filename_valid_names(self):
        """Verify that standard academic and document filenames are accepted."""
        valid_examples = [
            "DSA_assignment.txt", "Physics_lab_1.pdf", "resume_final.docx",
            "notes-unit2.txt", "my.presentation.pptx"
        ]
        for name in valid_examples:
            valid, err = is_valid_filename(name)
            self.assertTrue(valid, f"Expected '{name}' to be valid. Error was: {err}")

    def test_get_file_info(self):
        """Test metadata extraction from a single file."""
        sample_path = os.path.join(self.base_path, "test_doc.PDF")
        content = "Testing file information extraction."
        with open(sample_path, "w", encoding="utf-8") as f:
            f.write(content)

        info = get_file_info(sample_path)
        self.assertEqual(info["filename"], "test_doc.PDF")
        self.assertEqual(info["name"], "test_doc")
        self.assertEqual(info["ext"], ".pdf")  # normalized to lowercase
        self.assertEqual(info["size"], len(content.encode("utf-8")))
        self.assertGreater(info["modified_time"], 0)

    def test_scan_folder_recursive(self):
        """Test nested directory scanning and file collection."""
        sub_dir = os.path.join(self.base_path, "subfolder")
        os.makedirs(sub_dir)

        file1 = os.path.join(self.base_path, "file1.txt")
        file2 = os.path.join(sub_dir, "file2.txt")

        with open(file1, "w") as f:
            f.write("First file content")
        with open(file2, "w") as f:
            f.write("Second file content")

        scanned_path, files = scan_folder(self.base_path, verbose=False)
        self.assertEqual(scanned_path, self.base_path)
        self.assertEqual(len(files), 2)
        filenames = {f["filename"] for f in files}
        self.assertIn("file1.txt", filenames)
        self.assertIn("file2.txt", filenames)

    def test_calculate_directory_size_recursive(self):
        """
        Tests E9 recursive calculation of directory size.
        Verifies base case (single file) and recursive case (nested folders).
        """
        # Base case test: single file size
        single_file = os.path.join(self.base_path, "single.txt")
        with open(single_file, "w") as f:
            f.write("1234567890")  # 10 bytes
        self.assertEqual(calculate_directory_size_recursive(single_file), 10)

        # Recursive case test: nested folders
        nested_dir = os.path.join(self.base_path, "level1", "level2")
        os.makedirs(nested_dir)
        nested_file = os.path.join(nested_dir, "nested.txt")
        with open(nested_file, "w") as f:
            f.write("abcdefghij")  # 10 bytes

        expected_total = 20  # 10 bytes from single.txt + 10 bytes from nested.txt
        actual_total = calculate_directory_size_recursive(self.base_path)
        self.assertEqual(actual_total, expected_total)

if __name__ == "__main__":
    unittest.main()
