"""
SmartFile Renamer Module
Enables safe file renaming with keyword searching, filename validation,
extension preservation, overwrite collision checks, and history logging.
Protects original sample files in test_files/ from being modified during demo.
"""

import os
from utils import display_header, prompt_yes_no, is_valid_filename, format_size, get_project_path
from reporter import save_history
from scanner import scan_folder

def rename_file(files):
    """
    Interactively searches for a file and renames it safely.
    Protects original input sample files in test_files/ from alteration.
    Validates new name, prevents illegal characters, reserved Windows names,
    and accidental overwrites, preserves file extensions, and logs the action to history.

    Returns True if a file was successfully renamed, False otherwise.
    """
    display_header("Smart File Renamer")

    # If active files only contain test_files, offer organized_files or custom files
    test_dir = os.path.abspath(get_project_path("test_files"))
    org_dir = os.path.abspath(get_project_path("organized_files"))

    candidate_files = list(files) if files else []
    # If organized_files has files, also make them available for renaming
    if os.path.exists(org_dir):
        _, org_scanned = scan_folder(org_dir, verbose=False)
        if org_scanned:
            existing_paths = {f['path'] for f in candidate_files}
            for of in org_scanned:
                if of['path'] not in existing_paths:
                    candidate_files.append(of)

    if not candidate_files:
        print("No files loaded or found. Please scan files first (Menu option 1).")
        return False

    search_query = input("Enter part of the filename to search for renaming: ").strip().lower()
    if not search_query:
        print("Search query cannot be empty.")
        return False

    matches = [f for f in candidate_files if search_query in f['filename'].lower()]
    if not matches:
        print(f"No files matching '{search_query}' found.")
        return False

    print(f"\nFound {len(matches)} matching file(s):")
    print("-" * 75)
    for idx, match in enumerate(matches, start=1):
        try:
            rel = os.path.relpath(match['path'], get_project_path())
        except ValueError:
            rel = match['path']
        print(f"{idx}. {match['filename']} ({format_size(match['size'])})")
        print(f"   Location: {rel}")
    print("-" * 75)

    try:
        raw_choice = input("\nEnter file number to rename (or 0 to cancel): ").strip()
        choice = int(raw_choice)
        if choice == 0:
            print("Renaming cancelled.")
            return False
        if not (1 <= choice <= len(matches)):
            print(f"Invalid selection: please enter a number between 1 and {len(matches)}.")
            return False
        target_file = matches[choice - 1]
    except ValueError:
        print("Invalid input. Please enter a whole number.")
        return False

    target_path = os.path.abspath(target_file['path'])

    # Demo Protection: Do not modify pristine sample files in test_files/
    if target_path.startswith(test_dir):
        print("\n[Protection Notice] Input sample files in 'test_files/' are permanently protected")
        print("to ensure the demo environment remains intact for repeated presentations.")
        print("Please organize files first (Option 2) and rename the copy in 'organized_files/'.")
        return False

    current_filename = target_file['filename']
    current_dir = os.path.dirname(target_file['path'])
    orig_name, orig_ext = os.path.splitext(current_filename)

    print(f"\nSelected file: '{current_filename}'")
    new_input = input("Enter new filename (with or without extension): ").strip()

    valid, err_msg = is_valid_filename(new_input)
    if not valid:
        print(f"Invalid filename: {err_msg}")
        return False

    if '.' in new_input:
        dot_idx = new_input.rindex('.')
        new_base = new_input[:dot_idx]
        new_ext = new_input[dot_idx:]
    else:
        new_base = new_input
        new_ext = ""

    if not new_ext:
        final_new_name = new_input + orig_ext
        print(f"Note: Automatically preserving extension '{orig_ext}' -> '{final_new_name}'")
    else:
        final_new_name = new_input
        if new_ext.lower() != orig_ext.lower():
            print(f"Warning: Changing extension from '{orig_ext}' to '{new_ext}' may alter the file format.")
            if not prompt_yes_no("Are you sure you want to change the extension?"):
                print("Renaming cancelled.")
                return False

    if final_new_name == current_filename:
        print("The new filename is identical to the current filename. No rename needed.")
        return False

    dest_path = os.path.join(current_dir, final_new_name)

    if os.path.exists(dest_path):
        print(f"A file named '{final_new_name}' already exists in that folder. Renaming aborted to prevent overwrite.")
        return False

    print("\n" + "-" * 50)
    print("RENAME PREVIEW:")
    print(f"Old Name: {current_filename}")
    print(f"New Name: {final_new_name}")
    print(f"Location: {current_dir}")
    print("-" * 50)

    if not prompt_yes_no("Confirm renaming?"):
        print("Renaming cancelled by user.")
        return False

    try:
        os.rename(target_file['path'], dest_path)
    except FileNotFoundError:
        print("Error: The source file could not be found.")
        return False
    except PermissionError:
        print("Error: Permission denied. The file may be open in another application.")
        return False
    except OSError as e:
        print(f"OS error during renaming: {e}")
        return False
    else:
        save_history("Renamed", target_file['path'], dest_path)
        print(f"Success! File renamed to '{final_new_name}'.")
        return True
    finally:
        pass
