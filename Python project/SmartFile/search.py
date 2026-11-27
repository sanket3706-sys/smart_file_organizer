"""
SmartFile Search and Filter Module
Allows users to search and filter files in test_files/ and organized_files/
by keyword, extension, file size, or combined criteria without scanning unrelated project files.
"""

import os
from utils import display_header, format_size, get_project_path
from scanner import scan_folder

def get_demo_files_for_search(current_files=None):
    """
    Collects files from both test_files/ and organized_files/ for comprehensive searching,
    without scanning unrelated project directories.
    """
    combined = []
    seen_paths = set()

    if current_files:
        for f in current_files:
            if f['path'] not in seen_paths:
                combined.append(f)
                seen_paths.add(f['path'])

    # Also include organized_files if present
    org_dir = get_project_path("organized_files")
    if os.path.exists(org_dir):
        _, org_files = scan_folder(org_dir, verbose=False)
        if org_files:
            for f in org_files:
                if f['path'] not in seen_paths:
                    combined.append(f)
                    seen_paths.add(f['path'])

    return combined

def search_by_keyword(files, keyword):
    """
    Searches files whose filenames contain the given keyword or search tokens.
    Demonstrates E4 string methods:
    - .lower() and .upper()
    - .strip()
    - .split() (splitting multiple search terms)
    - .find() and .index() (locating character offsets)
    - .isupper() and .islower() (smart case matching)
    """
    term = keyword.strip()
    if not term:
        return []

    tokens = term.split()
    is_exact_case = term.isupper()

    matched = []
    for f in files:
        filename = f['filename']
        target_name = filename if is_exact_case else filename.lower()
        
        all_tokens_match = True
        for t in tokens:
            needle = t if is_exact_case else t.lower()
            if needle not in target_name:
                all_tokens_match = False
                break
            else:
                token_pos = target_name.index(needle)

        if all_tokens_match:
            matched.append(f)

    return matched

def search_by_extension(files, ext):
    """
    Searches files with matching extension.
    Demonstrates E4 string methods: .startswith(), .endswith(), .lower(), .upper(), .strip().
    """
    target = ext.strip()
    if not target.startswith('.'):
        target = '.' + target

    if target.isupper():
        return [f for f in files if f['filename'].endswith(target) or f['ext'].upper() == target]
    else:
        return [f for f in files if f['filename'].lower().endswith(target.lower())]

def filter_by_size(files, min_bytes=0, max_bytes=None):
    """
    Filters files based on minimum and maximum byte size.
    Demonstrates Course Concept E8: Lambda expressions and Python's built-in filter().
    """
    if max_bytes is not None:
        predicate = lambda f: min_bytes <= f['size'] <= max_bytes
    else:
        predicate = lambda f: f['size'] >= min_bytes
        
    return list(filter(predicate, files))

def display_search_results(results, query_desc=""):
    """
    Displays formatted search results with index numbers using enumerate().
    Shows file locations relative to project root.
    """
    print(f"\nSEARCH RESULTS for {query_desc}: {len(results)} file(s) found")
    print("-" * 75)
    if not results:
        print("No matching files found.")
        print("-" * 75)
        return

    print(f"{'#':<4} {'Filename':<30} {'Size':<12} {'Extension':<10}")
    print("-" * 75)
    for idx, f in enumerate(results, start=1):
        ext_display = f['ext'] if f['ext'] else "[none]"
        short_name = f['filename'][:28]
        try:
            rel_path = os.path.relpath(f['path'], get_project_path())
        except ValueError:
            rel_path = f['path']

        print(f"{idx:<4} {short_name:<30} {format_size(f['size']):<12} {ext_display:<10}")
        print(f"     Location: {rel_path}")
    print("-" * 75)

def search_files(files):
    """
    Interactive search and filter menu.
    Allows searching files across test_files/ and organized_files/.
    """
    display_header("Search and Filter Files")
    
    # Aggregate demo files (input test_files + organized_files)
    target_files = get_demo_files_for_search(files)
    if not target_files:
        print("No files available to search. Please scan files first (Menu option 1).")
        return

    while True:
        print("\nSelect Search / Filter Mode:")
        print("1. Search by Filename / Keyword")
        print("2. Search by File Extension")
        print("3. Filter by File Size (e.g. larger than X KB)")
        print("4. Combined Search (Keyword + Extension)")
        print("5. Return to Main Menu")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            kw = input("Enter search keyword or partial name: ").strip()
            if kw:
                results = search_by_keyword(target_files, kw)
                display_search_results(results, f"keyword '{kw}'")
            else:
                print("Keyword cannot be empty.")

        elif choice == "2":
            ext = input("Enter extension (e.g. 'txt', '.pdf'): ").strip()
            if ext:
                results = search_by_extension(target_files, ext)
                display_search_results(results, f"extension '{ext}'")
            else:
                print("Extension cannot be empty.")

        elif choice == "3":
            print("\nSize filter options:")
            print("a. Files larger than minimum size")
            print("b. Files smaller than maximum size")
            print("c. Files within a size range")
            sub_choice = input("Select option (a/b/c): ").strip().lower()

            try:
                if sub_choice == "a":
                    raw_val = input("Enter minimum size in KB: ").strip()
                    kb = float(raw_val)
                    results = filter_by_size(target_files, min_bytes=kb * 1024)
                    display_search_results(results, f"size >= {kb:.1f} KB")
                elif sub_choice == "b":
                    raw_val = input("Enter maximum size in KB: ").strip()
                    kb = float(raw_val)
                    results = filter_by_size(target_files, min_bytes=0, max_bytes=kb * 1024)
                    display_search_results(results, f"size <= {kb:.1f} KB")
                elif sub_choice == "c":
                    min_kb = float(input("Enter minimum size in KB: ").strip())
                    max_kb = float(input("Enter maximum size in KB: ").strip())
                    results = filter_by_size(target_files, min_bytes=min_kb * 1024, max_bytes=max_kb * 1024)
                    display_search_results(results, f"{min_kb:.1f} KB to {max_kb:.1f} KB")
                else:
                    print("Invalid size filter option.")
            except ValueError:
                print("Please enter a valid numeric value for size.")

        elif choice == "4":
            kw = input("Enter keyword: ").strip()
            ext = input("Enter extension: ").strip()
            filtered = target_files
            if kw:
                filtered = search_by_keyword(filtered, kw)
            if ext:
                filtered = search_by_extension(filtered, ext)
            display_search_results(filtered, f"keyword '{kw}' and extension '{ext}'")

        elif choice == "5":
            break
        else:
            print("Invalid selection. Please choose 1 to 5.")
