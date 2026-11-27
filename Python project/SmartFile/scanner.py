"""
SmartFile Scanner Module
Scans target directories, collects detailed file metadata,
excludes internal project directories, and demonstrates recursion.
Defaults automatically to the test_files/ demo input folder.
"""

import os
from utils import display_header, format_size, get_project_path

DEFAULT_INPUT_DIR = get_project_path("test_files")

# Directories that must never be scanned as input data
EXCLUDED_DIRS = {
    "organized_files", "data", "reports", "tests",
    ".git", "__pycache__", ".system_generated", "venv", ".venv"
}

def validate_folder(folder_path):
    """
    Validates if a given folder path exists, is a directory, and is accessible.
    Demonstrates conditional statements, exception handling, and input validation.
    """
    if not folder_path or not isinstance(folder_path, str):
        return False, "Folder path cannot be empty."
    
    clean_path = folder_path.strip().strip('"').strip("'")
    if not clean_path:
        return False, "Folder path cannot be empty."
        
    try:
        if not os.path.exists(clean_path):
            return False, f"Path does not exist: '{clean_path}'"
        if not os.path.isdir(clean_path):
            return False, f"Path is not a directory: '{clean_path}'"
        os.listdir(clean_path)
    except PermissionError:
        return False, f"Permission denied: cannot access '{clean_path}'."
    except OSError as e:
        return False, f"OS error accessing path: {e}"
        
    return True, clean_path

def get_file_info(filepath):
    """
    Extracts metadata for a single file.
    Returns a dictionary containing filename, name, extension, path, size, and modification time.
    """
    stat = os.stat(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    return {
        "filename": filename,
        "name": name,
        "ext": ext.lower().strip(),
        "path": os.path.abspath(filepath),
        "size": stat.st_size,
        "modified_time": stat.st_mtime
    }

def calculate_directory_size_recursive(path):
    """
    Recursively calculates the total storage size of all files in a folder tree.
    
    Demonstrates Course Concept E9 (Recursion):
    - Base Case 1: If path is a regular file, return its size directly (os.path.getsize).
    - Base Case 2: If a folder is empty or inaccessible, return 0.
    - Recursive Case: If path is a directory, iterate through child entries. For subdirectories,
      make a recursive call to calculate_directory_size_recursive(child_path) and accumulate the result.
    - Termination & Safety: Terminates when all files and leaf directories have been visited.
      Safely catches PermissionError, FileNotFoundError, and OSError without crashing.
    """
    total_bytes = 0
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
            
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total_bytes += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        if entry.name.lower() in EXCLUDED_DIRS:
                            continue
                        total_bytes += calculate_directory_size_recursive(entry.path)
                    else:
                        pass  # E5 loop control 'pass'
                except (PermissionError, FileNotFoundError, OSError):
                    continue
    except (PermissionError, FileNotFoundError, OSError):
        return 0
        
    return total_bytes

def scan_folder(folder_path=None, verbose=True):
    """
    Scans a folder and its nested subdirectories, collecting file information.
    Defaults to test_files/ so user does not need to enter paths repeatedly.
    Excludes organized_files/, data/, reports/, and tests/ from scanning.
    Handles inaccessible files safely without crashing.
    Returns: (cleaned_folder_path, list_of_file_info_dicts) or (None, None) on failure.
    """
    if not folder_path:
        if verbose:
            display_header("Folder Scanner")
            print(f"Default demo folder: test_files/")
        folder_input = input("Enter folder path to scan [Press Enter for default]: ").strip()
        if not folder_input:
            folder_input = DEFAULT_INPUT_DIR
    else:
        folder_input = folder_path

    valid, result = validate_folder(folder_input)
    if not valid:
        if verbose:
            print(f"Error: {result}")
        return None, None

    cleaned_folder = os.path.abspath(result)
    
    try:
        rel_display = os.path.relpath(cleaned_folder, get_project_path())
    except ValueError:
        rel_display = cleaned_folder

    if verbose:
        print(f"Scanning folder: {rel_display}/ ...")

    files = []
    total_size = 0
    total_folders = 0
    skipped_count = 0

    try:
        for root, dirs, filenames in os.walk(cleaned_folder):
            # Prune excluded directories so they are never visited
            dirs[:] = [d for d in dirs if d.lower() not in EXCLUDED_DIRS]
            total_folders += len(dirs)
            
            for fname in filenames:
                fpath = os.path.join(root, fname)
                try:
                    info = get_file_info(fpath)
                    files.append(info)
                    total_size += info["size"]
                except (PermissionError, FileNotFoundError, OSError) as e:
                    skipped_count += 1
                    if verbose:
                        print(f"Skipping inaccessible file '{fname}': {e}")
                    continue
    except Exception as e:
        if verbose:
            print(f"Error scanning folder: {e}")
        return None, None

    if verbose:
        print("\n" + "-" * 40)
        print("SCAN COMPLETE")
        print("-" * 40)
        print(f"Scanned folder:      {rel_display}/")
        print(f"Total files found:   {len(files)}")
        print(f"Total subfolders:    {total_folders}")
        print(f"Total storage used:  {format_size(total_size)}")
        if skipped_count > 0:
            print(f"Skipped files:       {skipped_count} (due to permissions/missing)")
        
        rec_size = calculate_directory_size_recursive(cleaned_folder)
        print(f"Recursive verified:  {format_size(rec_size)}")
        print("-" * 40)

    return cleaned_folder, files
