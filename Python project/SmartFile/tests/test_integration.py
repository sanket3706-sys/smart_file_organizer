"""
Integration Verification Script for SmartFile
Executes end-to-end integration tests on all modules using the permanent demo environment.
"""

import os
import sys
import shutil
import tempfile

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from scanner import scan_folder
from organizer import classify_file, determine_destination, preview_organization, organize_files, reset_organized_folder
from duplicate_detector import detect_duplicates
from search import search_by_keyword, search_by_extension, filter_by_size
from renamer import is_valid_filename
from recent_files import filter_recent_files
from analyzer import analyze_folder
from reporter import save_inventory_and_report
from rules_manager import load_rules

def run_integration_tests():
    test_dir = os.path.join(PROJECT_DIR, "test_files")
    org_dir = os.path.join(PROJECT_DIR, "organized_files")

    # Test 1: Scan test_files
    print("[1] Testing scan_folder on test_files...")
    folder, files = scan_folder(test_dir, verbose=False)
    assert folder is not None and len(files) == 9, f"Expected 9 files in test_files, got {len(files)}"
    print("    Scan passed: 9 files found.")

    # Test 2: Duplicate detection (duplicate1.txt & duplicate2.txt)
    print("[2] Testing duplicate detection on duplicate1.txt and duplicate2.txt...")
    dups = detect_duplicates(files)
    assert len(dups["confirmed_groups"]) == 1, f"Expected 1 confirmed group, got {len(dups['confirmed_groups'])}"
    conf_names = {f["filename"] for f in dups["confirmed_groups"][0]}
    assert "duplicate1.txt" in conf_names and "duplicate2.txt" in conf_names
    # Verify confirmed duplicate group is not mislabeled as potential
    for pgrp in dups["potential_groups"]:
        pnames = {f["filename"] for f in pgrp}
        assert "duplicate1.txt" not in pnames and "duplicate2.txt" not in pnames, "Confirmed files must not be in potential group"
    print("    Duplicate detection passed: duplicate1.txt & duplicate2.txt confirmed as identical via SHA-256.")

    # Test 3: Search
    print("[3] Testing search functions...")
    dsa_files = search_by_keyword(files, "dsa")
    assert len(dsa_files) == 1, f"Expected 1 DSA file, got {len(dsa_files)}"
    split_search = search_by_keyword(files, "python notes")
    assert len(split_search) == 1
    large_files = filter_by_size(files, min_bytes=400)
    assert len(large_files) >= 1
    print("    Search passed: Keyword, multi-token split, and size filters validated.")

    # Test 4: Renamer validation
    print("[4] Testing renamer validation...")
    ok, _ = is_valid_filename("valid_name.txt")
    bad_char, _ = is_valid_filename("bad:name*?.txt")
    con_bad, _ = is_valid_filename("CON.txt")
    aux_bad, _ = is_valid_filename("aux.pdf")
    trailing_dot, _ = is_valid_filename("test.")
    assert ok and not bad_char and not con_bad and not aux_bad and not trailing_dot
    print("    Renamer validation passed: Reserved Windows names and illegal characters rejected.")

    # Test 5: Recent files calendar-day
    print("[5] Testing recent files...")
    recent_today = filter_recent_files(files, mode_days=0)
    assert len(recent_today) == 9
    print("    Recent files passed: Calendar-day filter verified.")

    # Test 6: Analyzer
    print("[6] Testing analyzer...")
    analysis = analyze_folder(files, show_display=False, interactive=False)
    assert analysis["total_files"] == 9
    assert analysis["largest_file"] is not None
    assert analysis["smallest_file"] is not None
    print("    Analyzer passed: Metrics, extensions, and extremes verified.")

    # Test 7: Reporter
    print("[7] Testing report generation...")
    rep_ok = save_inventory_and_report(folder, files, analysis, dups)
    assert rep_ok
    assert os.path.exists(os.path.join(PROJECT_DIR, "data", "inventory.csv"))
    assert os.path.exists(os.path.join(PROJECT_DIR, "reports", "file_report.txt"))
    print("    Reporter passed: CSV and TXT reports created.")

    # Test 8: Non-destructive copy organization in temporary directory
    print("[8] Testing non-destructive copy organization and repeated-run idempotency...")
    with tempfile.TemporaryDirectory() as tmp_output:
        rules = load_rules()
        moves = preview_organization(files, tmp_output, rules)
        assert len(moves) == 9, f"Expected 9 moves on first run, got {len(moves)}"

        # Perform copy
        for src, dst, dst_dir in moves:
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src, dst)

        # 8a: Verify input test_files are UNCHANGED
        for f in files:
            assert os.path.exists(f["path"]), f"Input file was unexpectedly modified or moved: {f['path']}"

        # 8b: Verify organized structure in output
        assert os.path.exists(os.path.join(tmp_output, "College", "DSA", "Assignments", "DSA_assignment.txt"))
        assert os.path.exists(os.path.join(tmp_output, "College", "DBMS", "Notes", "DBMS_notes.txt"))
        assert os.path.exists(os.path.join(tmp_output, "College", "Python", "Notes", "Python_notes.txt"))
        assert os.path.exists(os.path.join(tmp_output, "College", "Mathematics", "Assignments", "maths_assignment.docx"))
        assert os.path.exists(os.path.join(tmp_output, "Documents", "resume.pdf"))
        assert os.path.exists(os.path.join(tmp_output, "Images", "photo.jpg"))

        # 8c: Repeated run idempotency check
        moves_2 = preview_organization(files, tmp_output, rules)
        assert len(moves_2) == 0, f"Repeated run should find 0 new moves, got {len(moves_2)}"
        assert moves_2.already_organized == 9, f"Expected 9 already organized, got {moves_2.already_organized}"
        print("    Organization passed: Copied cleanly, input files untouched, repeated run idempotent.")

    # Test 9: Two files with identical filenames from different folders
    print("[9] Testing collision prevention with identical filenames from different folders...")
    with tempfile.TemporaryDirectory() as collision_dir:
        input_a = os.path.join(collision_dir, "InputA")
        input_b = os.path.join(collision_dir, "InputB")
        out_dir = os.path.join(collision_dir, "Output")
        os.makedirs(input_a)
        os.makedirs(input_b)
        os.makedirs(out_dir)

        file_a = os.path.join(input_a, "DSA_assignment.txt")
        file_b = os.path.join(input_b, "DSA_assignment.txt")

        with open(file_a, "w", encoding="utf-8") as f:
            f.write("Section A assignment solutions")
        with open(file_b, "w", encoding="utf-8") as f:
            f.write("Section B assignment solutions")

        c_files = [
            {"filename": "DSA_assignment.txt", "path": file_a, "size": 30, "ext": ".txt"},
            {"filename": "DSA_assignment.txt", "path": file_b, "size": 30, "ext": ".txt"}
        ]

        rules = load_rules()
        c_moves = preview_organization(c_files, out_dir, rules)
        assert len(c_moves) == 2

        dest_a = c_moves[0][1]
        dest_b = c_moves[1][1]
        assert dest_a != dest_b, f"Colliding destinations: {dest_a} == {dest_b}"
        assert os.path.basename(dest_a) == "DSA_assignment.txt"
        assert os.path.basename(dest_b) == "DSA_assignment_1.txt"

        for src, dst, dst_d in c_moves:
            os.makedirs(dst_d, exist_ok=True)
            shutil.copy2(src, dst)

        assert os.path.exists(dest_a)
        assert os.path.exists(dest_b)
        assert os.path.exists(file_a)  # source A preserved
        assert os.path.exists(file_b)  # source B preserved
        print("    Collision test passed: Unique suffixes assigned, input files preserved.")

    print("\nALL INTEGRATION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_integration_tests()
