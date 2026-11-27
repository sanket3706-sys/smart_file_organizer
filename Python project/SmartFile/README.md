# SmartFile — Automatic File & Notes Organizer

A robust, modular, and explainable command-line file management and analytics suite designed for organizing academic notes, laboratory reports, assignments, and documents. Developed for the **Computational Thinking and Programming** course, this project demonstrates foundational and intermediate Python programming principles (Modules E3 through E10).

---

## 1. Project Introduction & Purpose
**SmartFile** is an automated desktop assistant that scans, organizes, inspects, and analyzes collections of files. Designed with a built-in demo environment, it uses:
- Configurable keyword rules loaded from `data/rules.csv`.
- Non-destructive copying (`shutil.copy2()`) that preserves original input files untouched.
- Cryptographic SHA-256 content hashing to accurately detect identical files.
- Recursive directory metrics (**E9 Recursion**) and collection processing (**E6, E7, E8**).
- Idempotent organization: running organization multiple times does not create redundant copies.

---

## 2. Problem Statement & Objectives
Students and instructors frequently handle cluttered folders containing lecture notes, lab sheets, assignments, images, and duplicate downloads. SmartFile provides:
1. **Rule-Based Organization:** Categorizes files into academic subjects (`College/DSA/`, `College/DBMS/`, `College/Physics/`, `College/Python/`, `College/Mathematics/`) and subcategories (`Assignments/`, `Notes/`, `Lab/`, `Projects/`, `Presentations/`), with extension fallbacks (`Documents/`, `Images/`).
2. **Preservation of Source Files:** Uses non-destructive copying (`shutil.copy2()`) from `test_files/` to `organized_files/`, preserving original timestamps and content.
3. **Collision Safety:** Prevents accidental overwrites by allocating unique numerical suffixes (`_1`, `_2`) if filenames collide.
4. **Idempotent Repeated Runs:** Recognizes files that have already been organized so repeat demonstrations do not produce redundant duplicates.
5. **Accurate Duplicate Detection:** Groups files by byte size and confirms identical contents using chunked SHA-256 cryptographic hashing without false-positive grouping.

---

## 3. Permanent Demo Environment
The application is pre-configured with a dedicated demo sandbox:

- **`test_files/` (Input Directory):** Contains 9 unsorted sample files with realistic academic text and genuine file formats:
  - `DSA_assignment.txt`: AVL tree and heap assignment questions.
  - `DBMS_notes.txt`: Transactions, ACID properties, and locking notes.
  - `Python_notes.txt`: Core Python course revision notes.
  - `duplicate1.txt` & `duplicate2.txt`: Byte-for-byte identical files for verifying SHA-256 duplicate detection.
  - `project_report.txt`: SmartFile documentation summary.
  - `resume.pdf`: Valid, openable PDF document.
  - `photo.jpg`: Valid, openable JPEG image.
  - `maths_assignment.docx`: Valid OpenXML DOCX document package.
- **`organized_files/` (Output Directory):** Automatically created output folder where SmartFile organizes files into their respective subject and subcategory directories.

---

## 4. Project Architecture & Folder Structure

```text
SmartFile/
│
├── main.py                     # Main interactive CLI application
├── scanner.py                  # Folder scanner and recursive size calculator
├── organizer.py                # Rule-based file classifier and non-destructive copy engine
├── analyzer.py                 # File statistics and distribution analyzer
├── duplicate_detector.py       # Two-stage SHA-256 duplicate detection engine
├── search.py                   # Multi-token keyword, extension, and size search
├── renamer.py                  # Safe file renamer with Windows reserved name validation
├── recent_files.py             # Calendar-day and rolling recent file tracker
├── reporter.py                 # Inventory CSV and summary TXT report generator
├── rules_manager.py            # CSV rule manager (view, add, remove, reset)
├── setup_demo.py               # Demo environment generator and reset utility
├── utils.py                    # Shared path, formatting, and validation helpers
│
├── test_files/                 # Permanent demo input folder (preserved untouched)
│   ├── DBMS_notes.txt
│   ├── DSA_assignment.txt
│   ├── duplicate1.txt
│   ├── duplicate2.txt
│   ├── maths_assignment.docx
│   ├── photo.jpg
│   ├── project_report.txt
│   ├── Python_notes.txt
│   └── resume.pdf
│
├── organized_files/            # Output folder populated by SmartFile
│   ├── College/
│   │   ├── DBMS/Notes/
│   │   ├── DSA/Assignments/
│   │   ├── Mathematics/Assignments/
│   │   └── Python/Notes/
│   ├── Documents/
│   └── Images/
│
├── data/                       # Application persistent data
│   ├── rules.csv               # Configurable classification rules
│   ├── inventory.csv           # Exported file inventory
│   └── organization_history.csv# Audit log of file operations
│
├── reports/                    # Generated summary reports
│   └── file_report.txt         # Human-readable folder analysis report
│
├── tests/                      # Automated unittest test suite
│   ├── test_scanner.py         # Unit tests for scanner, recursion, and reserved names
│   ├── test_organizer.py       # Unit tests for classification, destination & collision
│   ├── test_analyzer.py        # Unit tests for folder metrics and zip pairing
│   ├── test_duplicate_detector.py # Unit tests for SHA-256 duplicate detection
│   ├── test_search.py          # Unit tests for search, split tokens, and lambda filtering
│   ├── test_reporter.py        # Unit tests for CSV/TXT report generation
│   ├── test_integration.py     # End-to-end integration test suite
│   └── test_cases.txt          # Traceability matrix and test specifications
│
└── README.md                   # Comprehensive project documentation
```

---

## 5. Python Concepts Used (Mapped to E3–E10)

### E3 – Module Review
- **Variables & I/O:** Interactive `input()` handling and structured terminal output in `main.py`, `utils.py`, `search.py`.
- **Type Conversion:** Converting user inputs using `int()` and `float()` (e.g., choice selections, KB size thresholds).
- **Operators:** Arithmetic scaling (`utils.format_size()`), percentage calculations (`(count / total) * 100`), and logical operators (`and`, `or`, `not`).
- **Conditionals & Loops:** `if / elif / else` structures across all modules; `while True:` interactive event loops with clean `break` statements.

### E4 – String Slicing and String Methods
- **Slicing & Indexing:** Truncating file paths (`folder_display[-37:]`), table entries (`filename[:28]`), and hash snippets (`sample_hash[:16]`).
- **Case Transformation:** `.lower()` for case-insensitivity, `.upper()` for extensions and headers, `.title()` and `.capitalize()` for category standardizing.
- **Whitespace Cleaning:** `.strip()` applied to all inputs, filenames, and CSV fields.
- **Token Splitting:** `.split()` used in `search.py` to parse multi-keyword queries and in `organizer.py` to split filename tokens (`clean_name.split('_')`).
- **Substring Finding & Offsets:** `.find()` and `.index()` in `search.py` to locate keyword match offsets; `.rindex('.')` in `renamer.py` to locate extension boundaries.
- **Character Classification:** `.isupper()` and `.islower()` in `utils.clean_category_name()` to preserve uppercase acronyms (`DSA`, `DBMS`) while capitalizing lowercase names; `.isdigit()` for menu validation.

### E5 – Loop Control Statements
- **`for`:** Iterating over files, rules, directories, and search matches.
- **`while`:** Main menu event loop, input validation loops, and incrementing numerical counters in collision prevention (`while os.path.exists(...)`).
- **`break`:** Exiting loops upon user cancellation or finding target conditions.
- **`continue`:** Skipping already organized files, non-matching rules, and unreadable files.
- **`pass`:** Safe placeholder in non-fatal exception handlers.

### E6 – Membership, `enumerate()`, and `zip()`
- **Membership:** `if keyword in filename.lower()`, `if ext in EXTENSION_CATEGORIES["Images"]`.
- **`enumerate()`:** Generating numbered displays in `rules_manager.display_rules()`, `search.display_search_results()`, `recent_files.view_recent_files()`, and `renamer.rename_file()`.
- **`zip()`:** In `analyzer.py`, pairing sorted unique extension names with frequencies (`paired_ext_data = list(zip(ext_names, ext_frequencies))`).

### E7 – Integrated Collection Processing
- **Lists:** Ordered sequences of file dictionaries, rule dictionaries, and move tuples.
- **Tuples:** Immutable representation of move tuples `(src, dest, dest_folder)` and size/extension pairs.
- **Dictionaries:** File metadata structures (`filename`, `ext`, `size`, `path`, `modified_time`) and `.get(key, default)` lookups.
- **Sets & Set Operations:** In `analyzer.py`, `detected_extensions_set = set(ext_counts.keys())` and set difference `.difference()` against standard academic types; in `organizer.py`, `reserved_destinations = set()` preventing same-batch destination collisions.

### E8 – Lambda, `map()`, and `filter()`
- **Lambda Functions:** Custom sorting and selection keys:
  - `max(files, key=lambda x: x['size'])`
  - `min(files, key=lambda x: x['size'])`
  - `sorted(filtered, key=lambda f: f['modified_time'], reverse=True)`
- **`filter()`:** In `search.py`, filtering files by size threshold:
  `list(filter(lambda f: min_bytes <= f['size'] <= max_bytes, files))`
- **`map()`:** In `analyzer.py`, mapping file sizes into megabytes:
  `list(map(lambda f: round(f['size'] / (1024 * 1024), 4), files))`

### E9 – Recursion
- **Function:** `calculate_directory_size_recursive(path)` in `scanner.py`.
- **Base Cases:**
  1. Path is a single file (`os.path.isfile(path)`): returns `os.path.getsize(path)` immediately.
  2. Directory is empty or inaccessible: returns 0.
- **Recursive Case:** For directories, iterates through entries; when an entry is a subdirectory, makes a recursive call to `calculate_directory_size_recursive(entry.path)` and accumulates the returned size.
- **Safety & Termination:** Catches `PermissionError`, `FileNotFoundError`, and `OSError` without crashing.

### E10 – Exception Handling
- **Keywords:** `try`, `except`, `else`, `finally`, `raise`.
- **Specific Handlers:** Handlers specifically targeting `FileNotFoundError`, `PermissionError`, `ValueError`, `FileExistsError`, `csv.Error`, `shutil.Error`, and `OSError`.
- **Demonstration:**
  - `renamer.rename_file()` uses `try ... except ... else ... finally`.
  - `utils.ensure_dir()` handles `FileExistsError` and `PermissionError`.
  - `reporter.py` and `rules_manager.py` guard against CSV and I/O errors.

---

## 6. Libraries Used
Only Python's built-in standard library is utilized:
- `os`: File system operations, directory creation, path manipulation, and status.
- `shutil`: Non-destructive copying (`shutil.copy2()`) and directory management.
- `csv`: Reading and writing rules, inventory, and history logs.
- `datetime`: Timestamp conversions, current date resolution, and calendar-day arithmetic.
- `hashlib`: Cryptographic SHA-256 calculation for confirmed duplicate detection.
- `tempfile`: Isolated sandbox creation for automated unit tests.
- `unittest`: Automated test framework.
- `sys`: CLI argument and system exit handling.

---

## 7. How to Install and Run
1. **Prerequisites:** Python 3.8 or higher.
2. **Open the Project Directory in Terminal or VS Code:**
   ```bash
   cd "SmartFile"
   ```
3. **Execute the Application:**
   ```bash
   python main.py
   ```

---

## 8. Interactive Menu Walkthrough
SmartFile presents an 11-option menu on startup:

1. **Option 1: Scan Files:** Automatically scans the default input folder `test_files/` (or an optional custom directory). Displays file count, subfolder count, and total storage verified with recursive calculation.
2. **Option 2: Organize Files:** Previews the organization into `organized_files/`. Asks for confirmation (`Y/N`) and safely copies files into categories (`College/DSA/Assignments/`, `College/DBMS/Notes/`, `Documents/`, `Images/`) using `shutil.copy2()`.
3. **Option 3: Search Files:** Provides search options across `test_files/` and `organized_files/` by keyword, extension, or size threshold.
4. **Option 4: Detect Duplicate Files:** Computes chunked SHA-256 hashes and groups identical files (`duplicate1.txt` and `duplicate2.txt`).
5. **Option 5: Rename File:** Safely renames an organized file with character validation, Windows reserved name checks, and extension preservation.
6. **Option 6: View Recent Files:** Displays files modified today (calendar-day logic since 00:00:00), or within the last 3, 7, or 30 days.
7. **Option 7: Analyze Folder:** Displays total storage, extension distribution with percentages, extreme files (largest/smallest), and allows size threshold filtering.
8. **Option 8: Generate Reports:** Exports `data/inventory.csv` and compiles human-readable `reports/file_report.txt`.
9. **Option 9: Manage Organization Rules:** Inspects, adds, removes, or resets classification rules saved in `data/rules.csv`.
10. **Option 10: View Organization History:** Displays the audit history log of file operations.
11. **Option 11: Exit:** Safely exits the application.

---

## 9. Resetting the Demo Output Safely
To reset the demonstration environment for repeated presentations:
- **From within the Main Menu:** Select Option 2 ("Organize Files"). If `organized_files/` contains organized files, choose Sub-option 2 ("Reset organized_files/").
- **From the Command Line:** Run the setup script:
  ```bash
  python setup_demo.py
  ```
  This empties `organized_files/` and verifies that all 9 pristine sample files in `test_files/` are ready for a fresh demonstration. Original input files in `test_files/` are never deleted.

---

## 10. How to Run Automated Tests

To run the complete automated unit test suite with verbose output:
```bash
python -m unittest discover -s tests -v
```

All 30 automated unit tests execute and pass:
- Scanner tests: valid/invalid paths, file metadata, recursive folder size, Windows reserved names rejection (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`, `CON.txt`), trailing dot/space checks.
- Organizer tests: rule classification, academic subject routing, extension fallbacks, unique filename generation, collision prevention across identical filenames from different source directories, and copy execution.
- Analyzer tests: metric calculations, extreme size identification, `zip()` data pairing, and empty folder safety.
- Duplicate detector tests: SHA-256 calculation, confirmed duplicate detection, ensuring confirmed groups are not marked as potential, and size-collision separation.
- Search tests: keyword lookup, multi-token split search, smart-case matching (`.isupper()`), dot-optional extension matching, and lambda size filters.
- Reporter tests: inventory CSV creation, TXT report generation, and history logging.

To run the end-to-end integration verification script:
```bash
python tests/test_integration.py
```
