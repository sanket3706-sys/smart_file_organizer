"""
SmartFile Organizer Module
Classifies files using configurable keyword rules, maps them to categories and subcategories,
previews organization, preserves original input files using shutil.copy2(),
prevents filename collisions, and ensures idempotent repeated demonstrations.
"""

import os
import shutil
from rules_manager import load_rules
from utils import display_header, prompt_yes_no, ensure_dir, format_size, get_project_path
from reporter import save_history
from duplicate_detector import calculate_sha256

DEFAULT_OUTPUT_DIR = get_project_path("organized_files")

# Predefined standard extension categories for fallback classification
EXTENSION_CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"},
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".csv", ".xlsx", ".xls"},
    "Presentations": {".pptx", ".ppt", ".key", ".odp"}
}

class MovePlan(list):
    """
    Subclass of list holding the planned file moves with metadata.
    Provides standard list iteration, indexing, and length while storing already_organized count.
    """
    def __init__(self, moves=(), already_organized=0):
        super().__init__(moves)
        self.already_organized = already_organized

def classify_file(filename, rules):
    """
    Classifies a file into a category and subcategory based on rule keywords.
    Evaluates all matching keywords to determine both subject/category
    (e.g. DSA, DBMS, Physics, Python, Mathematics) and subcategory (e.g. Assignments, Notes, Lab).

    Demonstrates string methods (.lower(), .strip(), .replace(), .split()), membership ('in'),
    and integrated dictionary/list processing.
    """
    clean_name = filename.lower().replace('-', '_').replace(' ', '_')
    name_tokens = clean_name.split('_')
    
    final_category = "Unsorted"
    final_subcategory = ""

    for rule in rules:
        keyword = rule.get('keyword', '').strip().lower()
        if not keyword:
            continue  # E5 loop control 'continue'

        if keyword in clean_name or keyword in name_tokens:
            rule_cat = rule.get('category', '').strip()
            rule_subcat = rule.get('subcategory', '').strip()

            if rule_cat and final_category == "Unsorted":
                final_category = rule_cat

            if rule_subcat and not final_subcategory:
                final_subcategory = rule_subcat

    return final_category, final_subcategory

def determine_destination(dest_base_folder, file_info, rules):
    """
    Determines the absolute destination directory path for an organized file.
    Applies subject classification, subcategory rules, and extension-based fallbacks.
    """
    if not dest_base_folder:
        dest_base_folder = DEFAULT_OUTPUT_DIR

    category, subcategory = classify_file(file_info['filename'], rules)
    ext = file_info.get('ext', '').lower()

    # Fallback to extension-based category if no specific subject rule matched
    if category == "Unsorted":
        matched_ext_cat = False
        for cat_name, ext_set in EXTENSION_CATEGORIES.items():
            if ext in ext_set:
                category = cat_name
                matched_ext_cat = True
                break
        if not matched_ext_cat:
            category = "Unsorted"

    # Academic/subject categories belong inside College/
    academic_categories = {"DSA", "DBMS", "Physics", "Mathematics", "Python"}
    if category in academic_categories:
        dest_path = os.path.join(dest_base_folder, "College", category)
    else:
        dest_path = os.path.join(dest_base_folder, category)

    # Append subcategory folder if present (e.g., Assignments, Notes, Lab)
    if subcategory:
        dest_path = os.path.join(dest_path, subcategory)

    return os.path.abspath(dest_path)

def is_file_already_organized(src_path, dest_path):
    """
    Checks whether a destination file already exists and is identical to the source file.
    Ensures that repeated runs do not re-copy identical files or create redundant '_1' duplicates.
    Demonstrates exception handling and file size comparison.
    """
    if not os.path.exists(dest_path):
        return False
    try:
        if os.path.getsize(src_path) == os.path.getsize(dest_path):
            src_hash = calculate_sha256(src_path)
            dest_hash = calculate_sha256(dest_path)
            return src_hash is not None and src_hash == dest_hash
    except (PermissionError, FileNotFoundError, OSError):
        return False
    return False

def generate_unique_filename(dest_folder, filename, reserved_destinations=None):
    """
    Generates a unique destination path to prevent overwriting existing files on disk
    OR colliding with destination paths already assigned to other files in the same preview batch.
    """
    name, ext = os.path.splitext(filename)
    dest_path = os.path.join(dest_folder, filename)
    counter = 1

    while os.path.exists(dest_path) or (reserved_destinations is not None and dest_path in reserved_destinations):
        new_filename = f"{name}_{counter}{ext}"
        dest_path = os.path.join(dest_folder, new_filename)
        counter += 1

    return dest_path

def preview_organization(files, dest_base_folder=None, rules=None):
    """
    Previews all file copy operations before execution.
    Maintains a set of reserved destination paths to ensure that identical filenames
    from different source directories receive distinct, collision-free destination paths.
    Identifies files already organized to make repeated demonstrations safe and idempotent.

    Returns: MovePlan (list of move tuples with .already_organized attribute)
    """
    if not dest_base_folder:
        dest_base_folder = DEFAULT_OUTPUT_DIR
    if rules is None:
        rules = load_rules()

    display_header("Organization Preview")
    moves = []
    reserved_destinations = set()
    already_organized = 0

    for file in files:
        dest_folder = determine_destination(dest_base_folder, file, rules)
        natural_dest = os.path.join(dest_folder, file['filename'])

        # Check if the file was already organized in a previous run
        if is_file_already_organized(file['path'], natural_dest):
            already_organized += 1
            reserved_destinations.add(natural_dest)
            continue

        # Allocate unique destination path ensuring no collision with disk files or reserved paths
        dest_path = generate_unique_filename(dest_folder, file['filename'], reserved_destinations=reserved_destinations)
        
        # Check if it was already organized with this unique destination
        if is_file_already_organized(file['path'], dest_path):
            already_organized += 1
            reserved_destinations.add(dest_path)
            continue

        reserved_destinations.add(dest_path)
        moves.append((file['path'], dest_path, dest_folder))

        try:
            rel_dest = os.path.relpath(dest_path, dest_base_folder)
        except ValueError:
            rel_dest = dest_path

        print(f"• {file['filename']} ({format_size(file['size'])})")
        print(f"  → organized_files/{rel_dest}")

    print("\n" + "-" * 50)
    print(f"Files to copy:      {len(moves)}")
    print(f"Already organized:  {already_organized}")
    print("-" * 50)

    return MovePlan(moves, already_organized=already_organized)

def reset_organized_folder(dest_base_folder=None, confirm=True):
    """
    Safely resets the organized_files/ demo output directory.
    Empties its contents so that organization can be demonstrated freshly from scratch.
    Never modifies input test_files/ or system files.
    """
    if not dest_base_folder:
        dest_base_folder = DEFAULT_OUTPUT_DIR

    if confirm:
        print(f"\nTarget folder to reset: {dest_base_folder}")
        if not prompt_yes_no("Are you sure you want to clear the organized_files folder?"):
            print("Reset cancelled.")
            return False

    try:
        if os.path.exists(dest_base_folder):
            for item in os.listdir(dest_base_folder):
                item_path = os.path.join(dest_base_folder, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
        ensure_dir(dest_base_folder)
        print("✓ Demo output folder 'organized_files/' has been safely reset.")
        return True
    except (PermissionError, OSError) as e:
        print(f"Error resetting organized folder: {e}")
        return False

def organize_files(files, dest_base_folder=None):
    """
    Interactively organizes files into organized_files/ using shutil.copy2().
    Preserves original input files in test_files/ completely untouched.
    Displays formatted results directly in the terminal.
    Returns True if files were copied, False otherwise.
    """
    display_header("Smart File Organizer")
    if not files:
        print("No files to organize. Please scan files first (Menu option 1).")
        return False

    if not dest_base_folder:
        dest_base_folder = DEFAULT_OUTPUT_DIR

    ensure_dir(dest_base_folder)
    rules = load_rules()
    moves = preview_organization(files, dest_base_folder, rules)
    already_organized = getattr(moves, "already_organized", 0)

    try:
        rel_output = os.path.relpath(dest_base_folder, get_project_path())
    except ValueError:
        rel_output = dest_base_folder

    if not moves:
        print(f"\nAll {len(files)} files are already organized in '{rel_output}/'.")
        print("\n" + "=" * 50)
        print("ORGANIZATION COMPLETED")
        print("=" * 50)
        print(f"Files scanned:     {len(files)}")
        print(f"Files organized:   0 (already up-to-date)")
        print(f"Files skipped:     {already_organized}")
        print(f"Errors:            0\n")
        print(f"Output location:   {rel_output}/")
        print("=" * 50)
        return False

    print(f"\nReady to copy {len(moves)} file(s) into '{rel_output}/'.")
    print("Note: Original input files will be preserved untouched (copy mode).")
    if not prompt_yes_no("Do you want to proceed with organizing these files?"):
        print("Organization cancelled by user. No files were copied.")
        return False

    print("\nCopying files into organized structure...")
    moved_count = 0
    failed_count = 0

    for src, dest, dest_folder in moves:
        try:
            ensure_dir(dest_folder)
            # Use shutil.copy2 to preserve file content and metadata without deleting source
            shutil.copy2(src, dest)
            save_history("Copied", src, dest)
            moved_count += 1
        except (shutil.Error, PermissionError, FileNotFoundError, OSError) as e:
            failed_count += 1
            print(f"Failed to copy '{os.path.basename(src)}': {e}")
        except Exception as e:
            failed_count += 1
            print(f"Unexpected error copying '{os.path.basename(src)}': {e}")

    # Display clear results as specified in Section 6
    print("\n" + "=" * 50)
    print("ORGANIZATION COMPLETED")
    print("=" * 50)
    print(f"Files scanned:     {len(files)}")
    print(f"Files organized:   {moved_count}")
    print(f"Files skipped:     {already_organized}")
    print(f"Errors:            {failed_count}\n")
    print(f"Output location:   {rel_output}/")
    print("=" * 50)

    return moved_count > 0
