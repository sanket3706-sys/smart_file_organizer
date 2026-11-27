"""
SmartFile Demo Setup Script
Creates and populates the permanent demo environment:
- test_files/ (9 sample input files with realistic text, valid PDF, valid JPEG, valid DOCX)
- organized_files/ (ensures output directory exists)
Can be run anytime to reset or re-populate test_files.
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(BASE_DIR, "test_files")
ORGANIZED_DIR = os.path.join(BASE_DIR, "organized_files")

def setup_demo_environment():
    os.makedirs(TEST_DIR, exist_ok=True)
    os.makedirs(ORGANIZED_DIR, exist_ok=True)

    # 1. DSA_assignment.txt
    with open(os.path.join(TEST_DIR, "DSA_assignment.txt"), "w", encoding="utf-8") as f:
        f.write(
            "Course: Data Structures and Algorithms\n"
            "Assignment #3: Balanced Binary Trees and Heaps\n\n"
            "1. Implement AVL tree insertion with rotations (LL, RR, LR, RL).\n"
            "2. Build a Min-Heap and demonstrate heap-sort on 15 random integers.\n"
            "3. Compare time complexities of Dijkstra and Bellman-Ford shortest path algorithms.\n"
        )

    # 2. DBMS_notes.txt
    with open(os.path.join(TEST_DIR, "DBMS_notes.txt"), "w", encoding="utf-8") as f:
        f.write(
            "Course: Database Management Systems\n"
            "Unit 4 Notes: Concurrency Control and Transactions\n\n"
            "- ACID Properties: Atomicity, Consistency, Isolation, Durability.\n"
            "- Two-Phase Locking (2PL) Protocol: Growing phase and shrinking phase.\n"
            "- Deadlock prevention (Wait-Die, Wound-Wait) and detection via wait-for graphs.\n"
        )

    # 3. Python_notes.txt
    with open(os.path.join(TEST_DIR, "Python_notes.txt"), "w", encoding="utf-8") as f:
        f.write(
            "Course: Computational Thinking and Programming\n"
            "Python Notes: Core Concepts (E3-E10)\n\n"
            "- E4: String methods (.lower(), .upper(), .split(), .index(), .isupper()).\n"
            "- E6: Membership ('in') and iteration (enumerate(), zip()).\n"
            "- E8: Functional tools (map, filter, lambda expressions).\n"
            "- E9: Recursion with safe termination and base cases.\n"
            "- E10: Robust exception handling (try / except / else / finally).\n"
        )

    # 4. duplicate1.txt and duplicate2.txt (identical content for SHA-256 duplicate detection)
    dup_text = (
        "REVISION REFERENCE CHEAT SHEET: CORE ALGORITHMS\n"
        "===============================================\n\n"
        "Algorithm Complexities:\n"
        "- Quicksort: Average O(n log n), Worst O(n^2), In-place.\n"
        "- Mergesort: Best, Average, Worst O(n log n), O(n) space.\n"
        "- Binary Search: O(log n) time, requires sorted sequence.\n\n"
        "This file is used to verify SHA-256 duplicate content detection.\n"
        "Any copy with identical text will have the exact same cryptographic hash.\n"
    )

    with open(os.path.join(TEST_DIR, "duplicate1.txt"), "w", encoding="utf-8") as f:
        f.write(dup_text)

    with open(os.path.join(TEST_DIR, "duplicate2.txt"), "w", encoding="utf-8") as f:
        f.write(dup_text)

    # 5. project_report.txt
    with open(os.path.join(TEST_DIR, "project_report.txt"), "w", encoding="utf-8") as f:
        f.write(
            "SMARTFILE PROJECT REPORT\n"
            "Final Submission: Automatic File & Notes Organizer\n"
            "Course: Computational Thinking and Programming\n"
            "Summary: Modular rule-based desktop organization system using Python standard library.\n"
        )

    # 6. resume.pdf (valid minimal PDF document)
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        b"4 0 obj << /Length 55 >> stream\n"
        b"BT /F1 14 Tf 72 712 Td (Anil Sharma - Computer Science Resume) Tj ET\n"
        b"endstream\nendobj\n"
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000244 00000 n \n0000000349 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n420\n%%EOF\n"
    )
    with open(os.path.join(TEST_DIR, "resume.pdf"), "wb") as f:
        f.write(pdf_bytes)

    # 7. photo.jpg (valid minimal JPEG image)
    jpg_bytes = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
    )
    with open(os.path.join(TEST_DIR, "photo.jpg"), "wb") as f:
        f.write(jpg_bytes)

    # 8. maths_assignment.docx (valid minimal DOCX zip package)
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:p><w:r><w:t>Mathematics Assignment 1: Linear Algebra and Calculus</w:t></w:r></w:p></w:body>'
        '</w:document>'
    )

    docx_path = os.path.join(TEST_DIR, "maths_assignment.docx")
    with zipfile.ZipFile(docx_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("word/document.xml", document_xml)

    print(f"Demo environment created successfully at:\n  Input:  {TEST_DIR}\n  Output: {ORGANIZED_DIR}")

if __name__ == "__main__":
    setup_demo_environment()
