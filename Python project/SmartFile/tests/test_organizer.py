"""
Unit Tests for SmartFile Organizer Module
Tests rule-based classification, destination resolution, unique filename generation,
reserved destination tracking in preview, collision prevention, and safe file movement.
"""

import os
import shutil
import sys
import tempfile
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from organizer import (
    classify_file,
    determine_destination,
    generate_unique_filename,
    preview_organization
)
from utils import ensure_dir

class TestOrganizer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = self.test_dir.name
        self.rules = [
            {"keyword": "dsa", "category": "DSA", "subcategory": ""},
            {"keyword": "dbms", "category": "DBMS", "subcategory": ""},
            {"keyword": "physics", "category": "Physics", "subcategory": ""},
            {"keyword": "math", "category": "Mathematics", "subcategory": ""},
            {"keyword": "assignment", "category": "", "subcategory": "Assignments"},
            {"keyword": "notes", "category": "", "subcategory": "Notes"},
            {"keyword": "lab", "category": "", "subcategory": "Lab"},
            {"keyword": "project", "category": "", "subcategory": "Projects"},
            {"keyword": "presentation", "category": "", "subcategory": "Presentations"}
        ]

    def tearDown(self):
        self.test_dir.cleanup()

    def test_classification_combined_rules(self):
        """
        Verify that classification does not stop at the first match and correctly
        combines subject category and subcategory.
        """
        # DSA + assignment
        cat, subcat = classify_file("DSA_assignment.pdf", self.rules)
        self.assertEqual(cat, "DSA")
        self.assertEqual(subcat, "Assignments")

        # DSA + notes
        cat, subcat = classify_file("DSA_unit2_notes.pdf", self.rules)
        self.assertEqual(cat, "DSA")
        self.assertEqual(subcat, "Notes")

        # DBMS + assignment
        cat, subcat = classify_file("DBMS_assignment.pdf", self.rules)
        self.assertEqual(cat, "DBMS")
        self.assertEqual(subcat, "Assignments")

        # Physics + lab
        cat, subcat = classify_file("Physics_lab.pdf", self.rules)
        self.assertEqual(cat, "Physics")
        self.assertEqual(subcat, "Lab")

    def test_determine_destination_academic(self):
        """Verify destination path generation for College subjects."""
        file_info = {"filename": "DSA_assignment.pdf", "ext": ".pdf"}
        dest = determine_destination(self.base_path, file_info, self.rules)
        expected = os.path.abspath(os.path.join(self.base_path, "College", "DSA", "Assignments"))
        self.assertEqual(dest, expected)

    def test_determine_destination_extension_fallbacks(self):
        """Verify destination fallback to Images, Documents, and Presentations."""
        # Image
        img_info = {"filename": "Screenshot.png", "ext": ".png"}
        dest_img = determine_destination(self.base_path, img_info, self.rules)
        self.assertEqual(dest_img, os.path.abspath(os.path.join(self.base_path, "Images")))

        # Document
        doc_info = {"filename": "Resume.docx", "ext": ".docx"}
        dest_doc = determine_destination(self.base_path, doc_info, self.rules)
        self.assertEqual(dest_doc, os.path.abspath(os.path.join(self.base_path, "Documents")))

        # Presentation
        ppt_info = {"filename": "slides.pptx", "ext": ".pptx"}
        dest_ppt = determine_destination(self.base_path, ppt_info, self.rules)
        self.assertEqual(dest_ppt, os.path.abspath(os.path.join(self.base_path, "Presentations")))

    def test_generate_unique_filename_disk_and_reserved(self):
        """
        Verify unique filename generation accounts for both existing disk files
        and destination paths already reserved in the preview batch.
        """
        folder = os.path.join(self.base_path, "target")
        os.makedirs(folder)

        # 1. Existing disk file test
        orig_file = os.path.join(folder, "sample.txt")
        with open(orig_file, "w") as f:
            f.write("original")

        unique_1 = generate_unique_filename(folder, "sample.txt")
        self.assertEqual(os.path.basename(unique_1), "sample_1.txt")

        # 2. In-memory reservation test (file does not yet exist on disk, but is reserved)
        reserved = {unique_1}
        unique_2 = generate_unique_filename(folder, "sample.txt", reserved_destinations=reserved)
        self.assertEqual(os.path.basename(unique_2), "sample_2.txt")

    def test_preview_organization_same_filename_different_folders(self):
        """
        CRITICAL TEST: Verify that two different files having the exact same filename
        coming from different source folders both receive unique destination paths in the preview,
        and both can be moved without overwriting either file.
        """
        folder_a = os.path.join(self.base_path, "FolderA")
        folder_b = os.path.join(self.base_path, "FolderB")
        os.makedirs(folder_a)
        os.makedirs(folder_b)

        file_a_path = os.path.join(folder_a, "DSA_assignment.txt")
        file_b_path = os.path.join(folder_b, "DSA_assignment.txt")

        content_a = "Content of DSA Assignment from Folder A"
        content_b = "Content of DSA Assignment from Folder B"

        with open(file_a_path, "w", encoding="utf-8") as f:
            f.write(content_a)
        with open(file_b_path, "w", encoding="utf-8") as f:
            f.write(content_b)

        files = [
            {"filename": "DSA_assignment.txt", "path": file_a_path, "size": len(content_a), "ext": ".txt"},
            {"filename": "DSA_assignment.txt", "path": file_b_path, "size": len(content_b), "ext": ".txt"}
        ]

        moves = preview_organization(files, self.base_path, self.rules)
        self.assertEqual(len(moves), 2)

        src_1, dest_1, dest_folder_1 = moves[0]
        src_2, dest_2, dest_folder_2 = moves[1]

        # Verify they have the same target folder
        self.assertEqual(dest_folder_1, dest_folder_2)
        # Verify the destinations are DISTINCT (no collision!)
        self.assertNotEqual(dest_1, dest_2)
        self.assertEqual(os.path.basename(dest_1), "DSA_assignment.txt")
        self.assertEqual(os.path.basename(dest_2), "DSA_assignment_1.txt")

        # Execute the moves
        ensure_dir(dest_folder_1)
        shutil.move(src_1, dest_1)
        ensure_dir(dest_folder_2)
        shutil.move(src_2, dest_2)

        # Verify both files exist on disk simultaneously without data loss
        self.assertTrue(os.path.exists(dest_1))
        self.assertTrue(os.path.exists(dest_2))

        with open(dest_1, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content_a)
        with open(dest_2, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content_b)

    def test_preview_organization_skips_already_organized(self):
        """Verify that preview skips files already in their destination folder."""
        organized_folder = os.path.join(self.base_path, "College", "DSA", "Assignments")
        os.makedirs(organized_folder)
        file_path = os.path.join(organized_folder, "DSA_assignment.pdf")
        with open(file_path, "w") as f:
            f.write("content")

        files = [{
            "filename": "DSA_assignment.pdf",
            "name": "DSA_assignment",
            "ext": ".pdf",
            "path": file_path,
            "size": 7
        }]

        moves = preview_organization(files, self.base_path, self.rules)
        self.assertEqual(len(moves), 0)

if __name__ == "__main__":
    unittest.main()
