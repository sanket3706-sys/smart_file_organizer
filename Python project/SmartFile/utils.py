"""
SmartFile Utility Module
Provides shared helper functions for path handling, input validation,
formatting, and directory management. Demonstrates E3, E4, and E10 concepts.
"""

import os
import datetime

# Determine base directory of the project so paths work regardless of current working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Windows reserved device names that cannot be used as file names (with or without extensions)
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}

def get_project_path(*subpaths):
    """
    Constructs an absolute path relative to the SmartFile project root.
    """
    return os.path.join(BASE_DIR, *subpaths)

def display_header(title):
    """
    Displays a standardized section header with title formatting.
    Demonstrates E4 string methods (.upper(), .strip()) and arithmetic repetition (*).
    """
    clean_title = title.strip()
    print("\n" + "=" * 50)
    print(clean_title.upper())
    print("=" * 50)

def prompt_yes_no(prompt_text):
    """
    Prompts the user for a Yes/No response with validation.
    Demonstrates while loop, .strip(), .lower(), membership 'in', and loop control.
    """
    while True:
        ans = input(f"{prompt_text} (Y/N): ").strip().lower()
        if ans in ['y', 'yes']:
            return True
        elif ans in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")

def ensure_dir(path):
    """
    Ensures that a directory exists; creates it if missing.
    Demonstrates E10 specific exception handling (FileExistsError, PermissionError, OSError).
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
    except FileExistsError:
        pass  # E5 loop control 'pass': directory was created concurrently
    except PermissionError:
        print(f"Permission denied: cannot create directory '{path}'")
        raise
    except OSError as e:
        print(f"OS error creating directory '{path}': {e}")
        raise

def format_size(size_bytes):
    """
    Formats a byte count into a readable string (Bytes, KB, MB, GB).
    Demonstrates type conversion, arithmetic operators, and string formatting.
    """
    if not isinstance(size_bytes, (int, float)):
        return "0 B"
    
    if size_bytes < 1024:
        return f"{int(size_bytes)} B"
    elif size_bytes < 1024 * 1024:
        kb = size_bytes / 1024
        return f"{kb:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        mb = size_bytes / (1024 * 1024)
        return f"{mb:.2f} MB"
    else:
        gb = size_bytes / (1024 * 1024 * 1024)
        return f"{gb:.2f} GB"

def format_timestamp(ts):
    """
    Converts a POSIX timestamp into a formatted date-time string.
    """
    try:
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, OSError):
        return "Unknown Date"

def is_valid_filename(filename):
    """
    Validates whether a filename contains valid characters and follows filesystem rules.
    Rejects:
    - Empty or whitespace-only names
    - Reserved Windows device names (CON, PRN, AUX, NUL, COM1-9, LPT1-9), with or without extensions
    - Filenames ending with a dot or trailing space
    - Reserved characters (< > : " / \\ | ? *)
    - Filenames exceeding 255 characters
    
    Demonstrates E4 string methods:
    - .strip()
    - .split()
    - .startswith() and .endswith()
    - .upper()
    - .count()
    - String indexing and slicing
    - membership 'in'
    """
    if not filename or not isinstance(filename, str):
        return False, "Filename cannot be empty."

    # Check for trailing dots or spaces in the original input
    if filename.endswith('.') or filename.endswith(' '):
        return False, "Filename cannot end with a dot or trailing space."

    cleaned = filename.strip()
    if not cleaned:
        return False, "Filename cannot be empty."

    # Prevent filenames consisting solely of dots (e.g. '.', '..', '...')
    if cleaned.startswith('.') and cleaned.count('.') == len(cleaned):
        return False, "Filename cannot consist solely of dots."

    # Check for reserved or invalid filesystem characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        if char in cleaned:
            return False, f"Filename contains invalid character: '{char}'"

    # Check Windows reserved device names (e.g., CON, PRN, AUX, NUL, COM1, LPT1)
    # Using .split('.') to extract the primary base name before any extension
    name_parts = cleaned.split('.')
    primary_name = name_parts[0].strip().upper()
    if primary_name in WINDOWS_RESERVED_NAMES:
        return False, f"Filename uses reserved Windows device name: '{primary_name}'"

    # Demonstrate string slicing: filename length limit check
    if len(cleaned) > 255:
        shortened = cleaned[:30] + "..."
        return False, f"Filename too long ({len(cleaned)} characters): '{shortened}'"

    return True, "Valid filename."

def clean_category_name(name):
    """
    Cleans and standardizes category or subcategory names.
    Preserves uppercase acronyms (e.g. 'DSA', 'DBMS') using .isupper(),
    title-cases lowercase input using .islower(), and splits multi-word names with .split().
    
    Demonstrates E4 .isupper(), .islower(), .split(), .title(), and .strip().
    """
    stripped = name.strip()
    if not stripped:
        return ""

    # Preserve all-uppercase acronyms (e.g., 'DSA', 'DBMS')
    if stripped.isupper():
        return stripped

    # If completely lowercase, convert to Title Case (e.g., 'physics' -> 'Physics')
    if stripped.islower():
        return stripped.title()

    # Multi-word string processing: split into tokens and standardize
    words = stripped.split()
    standardized_words = [w.title() if w.islower() else w for w in words]
    return " ".join(standardized_words)
