"""
SmartFile Duplicate Detection Module
Identifies duplicates reliably using a two-tier approach:
1. First groups files by size (files with size > 0 and same byte length).
2. Computes and compares SHA-256 hashes of file contents to confirm identical data.
Accurately separates confirmed duplicate groups from potential same-size/different-content groups.
Never deletes files automatically; presents clear, explainable findings.
"""

import os
import hashlib
from utils import display_header, format_size

def calculate_sha256(filepath, chunk_size=65536):
    """
    Computes the SHA-256 hash of a file reading in chunks.
    Chunked reading ensures minimal memory usage even for large files.
    Demonstrates E10 exception handling (FileNotFoundError, PermissionError, OSError) and hashlib.
    """
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break  # E5 loop control 'break'
                sha256.update(chunk)
        return sha256.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return None

def detect_duplicates(files):
    """
    Analyzes files and categorizes them into confirmed duplicates and potential duplicates.
    
    Rules:
    - Confirmed duplicates: 2 or more files with the exact same size AND identical SHA-256 hash.
    - Potential duplicates: 2 or more files with the exact same size whose SHA-256 hashes differ.
    - An entire size group is NEVER labeled as potential if files within it are already confirmed duplicates.
      Only files with distinct, non-duplicate hashes (singletons) sharing the same size are grouped as potential.

    Returns a dictionary:
    {
        "confirmed_groups": [ [file_info, ...], ... ],
        "potential_groups": [ [file_info, ...], ... ]
    }
    """
    if not files:
        return {"confirmed_groups": [], "potential_groups": []}

    # Step 1: Group files by byte size (ignoring empty 0-byte files for duplicate content)
    size_groups = {}
    for f in files:
        sz = f.get('size', 0)
        if sz > 0:
            if sz not in size_groups:
                size_groups[sz] = []
            size_groups[sz].append(f)

    # Filter to sizes having 2 or more files
    candidates = {sz: grp for sz, grp in size_groups.items() if len(grp) > 1}

    confirmed_groups = []
    potential_groups = []

    # Step 2: Compare file contents using SHA-256
    for sz, grp in candidates.items():
        hash_map = {}
        for file_info in grp:
            file_hash = calculate_sha256(file_info['path'])
            if file_hash is not None:
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(file_info)

        # Collect confirmed duplicate sets (2 or more files with identical content hash)
        for h, matching_files in hash_map.items():
            if len(matching_files) > 1:
                confirmed_groups.append(matching_files)

        # Potential duplicates: only files with distinct, non-matching hashes sharing this size
        # Never include files that are already confirmed duplicates
        singletons = [file_list[0] for file_list in hash_map.values() if len(file_list) == 1]
        if len(singletons) > 1:
            potential_groups.append(singletons)

    return {
        "confirmed_groups": confirmed_groups,
        "potential_groups": potential_groups
    }

def find_duplicates(files):
    """
    User-facing function to detect and display duplicate files.
    Explains why files are considered duplicates (exact SHA-256 hash match).
    """
    display_header("Duplicate File Detection")
    if not files:
        print("No files loaded. Please scan a folder first (Menu option 1).")
        return None

    print("Analyzing file sizes and computing SHA-256 hashes...")
    results = detect_duplicates(files)
    confirmed = results["confirmed_groups"]
    potential = results["potential_groups"]

    if not confirmed and not potential:
        print("\nNo duplicate files found in the scanned folder.")
        return results

    if confirmed:
        print(f"\n[CONFIRMED DUPLICATES] Found {len(confirmed)} group(s) with IDENTICAL content:")
        print("These files have the EXACT SAME SHA-256 hash and size.")
        print("-" * 60)
        for idx, group in enumerate(confirmed, start=1):
            sample_hash = calculate_sha256(group[0]['path'])
            hash_display = sample_hash[:16] if sample_hash else "unknown"
            print(f"Group #{idx} (Size: {format_size(group[0]['size'])}, Hash: {hash_display}...):")
            for f in group:
                print(f"  ✓ {f['filename']}")
                print(f"    Path: {f['path']}")
            print()
    else:
        print("\nNo confirmed duplicate files found with identical content.")

    if potential:
        print(f"\n[POTENTIAL DUPLICATES (SAME SIZE, DIFFERENT CONTENT)]: {len(potential)} group(s):")
        print("These files share the exact same byte size, but their contents differ.")
        print("-" * 60)
        for idx, group in enumerate(potential, start=1):
            print(f"Size Match #{idx} ({format_size(group[0]['size'])}):")
            for f in group:
                f_hash = calculate_sha256(f['path'])
                hash_snippet = f_hash[:12] if f_hash else "unreadable"
                print(f"  • {f['filename']} (Hash snippet: {hash_snippet}...)")
            print()

    print("=" * 60)
    print("SAFETY NOTICE: SmartFile never deletes duplicate files automatically.")
    print("Review the files manually before deciding to remove any copy.")
    print("=" * 60)

    return results
