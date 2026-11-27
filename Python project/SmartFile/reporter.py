"""
SmartFile Reporter Module
Generates structured inventory CSV reports, human-readable TXT summaries,
and maintains an audit history log of all file organization and renaming operations.
"""

import csv
import os
import datetime
from utils import ensure_dir, display_header, format_size, get_project_path

# Relative paths resolved safely through get_project_path
HISTORY_FILE = get_project_path("data", "organization_history.csv")
INVENTORY_FILE = get_project_path("data", "inventory.csv")
REPORT_FILE = get_project_path("reports", "file_report.txt")

def init_history():
    """
    Initializes the history CSV file with header columns if not present.
    """
    ensure_dir(get_project_path("data"))
    if not os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "time", "action", "original_path", "new_path"])
        except (PermissionError, csv.Error, OSError) as e:
            print(f"Error initializing history file: {e}")

def save_history(action, original_path, new_path):
    """
    Appends an operation (Moved, Renamed) to the audit history CSV.
    Demonstrates datetime formatting and CSV writing with specific exception handling.
    """
    init_history()
    now = datetime.datetime.now()
    try:
        with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                action,
                original_path,
                new_path
            ])
    except (PermissionError, csv.Error, OSError) as e:
        print(f"Warning: Could not save to history log: {e}")

def parse_history_row(row):
    """
    Safely unpacks a history row supporting both column orders:
    (date, time, action, src, dst) or (date, time, src, dst, action).
    Demonstrates membership testing and collection unpacking.
    """
    if len(row) < 5:
        return "Unknown", "Unknown", "Action", "", ""
    d, t = row[0], row[1]
    if row[2].lower() in ["moved", "renamed", "copied"]:
        action, src, dst = row[2], row[3], row[4]
    elif row[4].lower() in ["moved", "renamed", "copied"]:
        action, src, dst = row[4], row[2], row[3]
    else:
        action, src, dst = row[2], row[3], row[4]
    return d, t, action, src, dst

def get_recent_history(limit=10):
    """
    Reads the most recent N history entries.
    Demonstrates file reading, CSV parsing, and list slicing with specific exception handling.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            rows = list(reader)
            return rows[-limit:] if rows else []
    except (PermissionError, FileNotFoundError, csv.Error, OSError):
        return []

def view_history():
    """
    Displays recent organization and rename operations from the history log.
    Demonstrates E6 enumerate() and E4 string methods.
    """
    display_header("Organization History")
    if not os.path.exists(HISTORY_FILE):
        print("No organization history found. Perform an organization or rename operation first.")
        return

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            history = list(reader)

            if not history:
                print("Organization history is currently empty.")
                return

            print(f"Showing last {min(15, len(history))} of {len(history)} recorded action(s):")
            print("-" * 65)
            for idx, raw_row in enumerate(history[-15:], start=1):
                d, t, action, src, dst = parse_history_row(raw_row)
                print(f"{idx}. [{d} {t}] {action.upper()}:")
                print(f"   From: {src}")
                print(f"   To:   {dst}")
                print("-" * 45)
    except (PermissionError, FileNotFoundError, csv.Error, OSError) as e:
        print(f"Error reading history file: {e}")

def save_inventory_and_report(folder, files, analysis_data, duplicate_info=None):
    """
    Generates both inventory.csv and a detailed human-readable file_report.txt.
    Includes duplicate information and history when available.
    Demonstrates specific exception handling (PermissionError, FileNotFoundError, csv.Error, OSError).
    """
    display_header("Generate Inventory and Audit Report")
    if not files:
        print("No files available for reporting. Please scan a folder first (Menu option 1).")
        return False

    ensure_dir(get_project_path("data"))
    ensure_dir(get_project_path("reports"))

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # 1. Save Inventory CSV with specific exception handling
    try:
        with open(INVENTORY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["filename", "ext", "size_bytes", "path"])
            writer.writeheader()
            for file_info in files:
                writer.writerow({
                    "filename": file_info.get("filename", ""),
                    "ext": file_info.get("ext", ""),
                    "size_bytes": file_info.get("size", 0),
                    "path": file_info.get("path", "")
                })
        print(f"✓ Inventory CSV saved: {INVENTORY_FILE}")
    except (PermissionError, FileNotFoundError, csv.Error, OSError) as e:
        print(f"Error saving inventory CSV: {e}")
        return False

    # 2. Generate Detailed Text Report
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("              SMARTFILE INVENTORY & AUDIT REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated On:   {date_str}\n")
            f.write(f"Scanned Folder: {folder if folder else 'N/A'}\n")
            f.write(f"Total Files:    {len(files)}\n")

            total_size_bytes = analysis_data.get('total_size_bytes', sum(f.get('size', 0) for f in files))
            f.write(f"Total Storage:  {format_size(total_size_bytes)}\n\n")

            # File type summary
            f.write("------------------------------------------------------------\n")
            f.write("FILE TYPE DISTRIBUTION\n")
            f.write("------------------------------------------------------------\n")
            ext_counts = analysis_data.get('ext_counts', {})
            if ext_counts:
                for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True):
                    pct = (count / len(files)) * 100 if files else 0
                    f.write(f"  • {ext:<16} : {count:>4} files ({pct:.1f}%)\n")
            else:
                f.write("  No extension data available.\n")
            f.write("\n")

            # Largest and Smallest files
            f.write("------------------------------------------------------------\n")
            f.write("FILE SIZE EXTREMES\n")
            f.write("------------------------------------------------------------\n")
            largest = analysis_data.get('largest_file')
            if largest:
                f.write(f"Largest File:\n")
                f.write(f"  Name: {largest.get('filename')}\n")
                f.write(f"  Size: {format_size(largest.get('size', 0))}\n")
                f.write(f"  Path: {largest.get('path')}\n\n")

            smallest = analysis_data.get('smallest_file')
            if smallest:
                f.write(f"Smallest File:\n")
                f.write(f"  Name: {smallest.get('filename')}\n")
                f.write(f"  Size: {format_size(smallest.get('size', 0))}\n")
                f.write(f"  Path: {smallest.get('path')}\n\n")

            # Confirmed Duplicates section
            f.write("------------------------------------------------------------\n")
            f.write("DUPLICATE FILES AUDIT\n")
            f.write("------------------------------------------------------------\n")
            if duplicate_info and duplicate_info.get("confirmed_groups"):
                confirmed = duplicate_info["confirmed_groups"]
                f.write(f"Found {len(confirmed)} set(s) of confirmed duplicates (matching SHA-256):\n\n")
                for i, grp in enumerate(confirmed, 1):
                    f.write(f"Duplicate Set #{i} (Size: {format_size(grp[0].get('size', 0))}):\n")
                    for dfile in grp:
                        f.write(f"  - {dfile.get('filename')} ({dfile.get('path')})\n")
                    f.write("\n")
            else:
                f.write("No confirmed duplicates detected or duplicate audit was not run.\n\n")

            # Recent Organization History
            f.write("------------------------------------------------------------\n")
            f.write("RECENT ORGANIZATION HISTORY (Last 10 Actions)\n")
            f.write("------------------------------------------------------------\n")
            recent_hist = get_recent_history(10)
            if recent_hist:
                for row in recent_hist:
                    d, t, action, src, dst = parse_history_row(row)
                    f.write(f"[{d} {t}] {action.upper()}:\n")
                    f.write(f"   From: {src}\n")
                    f.write(f"   To:   {dst}\n")
            else:
                f.write("No organization history recorded yet.\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("                    END OF REPORT\n")
            f.write("=" * 60 + "\n")

        print(f"✓ Summary text report saved: {REPORT_FILE}")
        return True
    except (PermissionError, FileNotFoundError, OSError) as e:
        print(f"Error saving summary report: {e}")
        return False
