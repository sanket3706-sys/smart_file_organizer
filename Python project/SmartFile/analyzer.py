"""
SmartFile Analyzer Module
Computes detailed folder statistics: total files, total storage, unique extensions,
file type distribution, largest/smallest files, most common extension, files without
extension, and size threshold queries.

Demonstrates Course Concepts:
- E7: Lists, Tuples, Dictionaries, Sets (set union, intersection, difference).
- E8: Lambda expressions, map(), filter(), sorted(), max(), min().
- E6: zip() to pair extension names with their counts.
"""

from utils import display_header, format_size

def analyze_folder(files, show_display=True, interactive=False):
    """
    Performs comprehensive analysis on the list of scanned files.
    Returns a dictionary of analysis metrics.
    If interactive=True, allows the user to query files larger than a threshold.
    """
    if show_display:
        display_header("File Analyzer")

    if not files:
        if show_display:
            print("No files to analyze. Please scan a folder first (Menu option 1).")
        return {}

    total_files = len(files)
    total_size_bytes = sum(f['size'] for f in files)
    total_size_mb = total_size_bytes / (1024 * 1024)

    # Extension counting using dictionary .get()
    ext_counts = {}
    no_ext_count = 0
    all_extensions = []

    for f in files:
        ext = f.get('ext', '').strip().lower()
        if not ext:
            no_ext_count += 1
            category_key = "[no extension]"
        else:
            category_key = ext.upper()
        all_extensions.append(category_key)
        ext_counts[category_key] = ext_counts.get(category_key, 0) + 1

    # Demonstrate Sets and Set Operations (E7)
    detected_extensions_set = set(ext_counts.keys())
    standard_academic_types = {".PDF", ".DOCX", ".TXT", ".PPTX"}
    # Set difference: extensions present outside standard academic types
    non_standard_types = detected_extensions_set.difference(standard_academic_types)

    # Largest and Smallest files using max() and min() with lambda keys (E8)
    largest_file = max(files, key=lambda x: x['size']) if files else None
    smallest_file = min(files, key=lambda x: x['size']) if files else None

    # Most common extension using max() on dictionary
    most_common_ext = max(ext_counts, key=ext_counts.get) if ext_counts else "N/A"

    # Demonstrate zip() (E6): pair sorted extension names with their counts
    sorted_ext_items = sorted(ext_counts.items(), key=lambda item: item[1], reverse=True)
    ext_names = [item[0] for item in sorted_ext_items]
    ext_frequencies = [item[1] for item in sorted_ext_items]
    paired_ext_data = list(zip(ext_names, ext_frequencies))

    # Demonstrate map() (E8): compute sizes in MB for files
    sizes_in_mb = list(map(lambda f: round(f['size'] / (1024 * 1024), 4), files))

    if show_display:
        print("SUMMARY STATISTICS")
        print("-" * 45)
        print(f"Total Files:                 {total_files}")
        print(f"Total Storage Occupied:      {format_size(total_size_bytes)} ({total_size_mb:.2f} MB)")
        print(f"Unique File Types:           {len(detected_extensions_set)}")
        print(f"Files without Extension:     {no_ext_count}")
        print(f"Most Common File Type:       {most_common_ext} ({ext_counts.get(most_common_ext, 0)} files)")
        print("-" * 45)

        print("\nFILE TYPE DISTRIBUTION:")
        print(f"{'Extension':<18} {'Count':<8} {'Percentage':<10}")
        print("-" * 45)
        for ext_name, count in paired_ext_data:
            pct = (count / total_files) * 100
            print(f"{ext_name:<18} {count:<8} {pct:.1f}%")
        print("-" * 45)

        if largest_file:
            print(f"\nLargest File:")
            print(f"  • Name: {largest_file['filename']}")
            print(f"  • Size: {format_size(largest_file['size'])}")
            print(f"  • Path: {largest_file['path']}")

        if smallest_file:
            print(f"\nSmallest File:")
            print(f"  • Name: {smallest_file['filename']}")
            print(f"  • Size: {format_size(smallest_file['size'])}")
            print(f"  • Path: {smallest_file['path']}")

        # Interactive filter for files larger than a user-chosen size (E8 filter)
        if interactive:
            print("\n" + "=" * 45)
            query_threshold = input("View files larger than a specific size? (Enter size in KB or press Enter to skip): ").strip()
            if query_threshold:
                try:
                    threshold_kb = float(query_threshold)
                    threshold_bytes = threshold_kb * 1024
                    # Use filter() with lambda (E8)
                    large_files = list(filter(lambda f: f['size'] >= threshold_bytes, files))
                    print(f"\nFiles >= {threshold_kb:.1f} KB ({len(large_files)} found):")
                    for lf in sorted(large_files, key=lambda f: f['size'], reverse=True):
                        print(f"  • {lf['filename']} — {format_size(lf['size'])}")
                except ValueError:
                    print("Invalid number entered; skipping threshold listing.")

    return {
        "total_files": total_files,
        "total_size_bytes": total_size_bytes,
        "total_size_mb": total_size_mb,
        "unique_extensions": detected_extensions_set,
        "unique_extension_count": len(detected_extensions_set),
        "ext_counts": ext_counts,
        "no_ext_count": no_ext_count,
        "most_common_ext": most_common_ext,
        "largest_file": largest_file,
        "smallest_file": smallest_file,
        "paired_ext_data": paired_ext_data
    }
