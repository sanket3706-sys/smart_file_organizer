"""
SmartFile Recent Files Tracker Module
Filters and displays files modified recently: today (calendar-day logic),
last 3 days, last 7 days, or last 30 days.
"""

import datetime
from utils import display_header, format_size, format_timestamp

def filter_recent_files(files, mode_days):
    """
    Filters files based on modification timestamp.
    
    Mode parameter:
    - 0 or "today": Calendar-day logic (files modified since 00:00:00 of current local day).
    - 3, 7, 30: Rolling window of N days (N * 86400 seconds from current timestamp).

    Demonstrates E8 sorted(..., key=lambda ...) and lambda filtering.
    """
    now = datetime.datetime.now()

    if mode_days == 0 or mode_days == "today":
        # Calendar-day logic for Today: midnight of current date
        start_of_today = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
        cutoff_timestamp = start_of_today.timestamp()
    else:
        # Rolling N-day window
        cutoff_timestamp = now.timestamp() - (int(mode_days) * 86400)

    filtered = [f for f in files if f.get('modified_time', 0) >= cutoff_timestamp]
    # Sort files by modification time descending (newest first)
    return sorted(filtered, key=lambda f: f['modified_time'], reverse=True)

def view_recent_files(files):
    """
    Interactive menu to view recently modified files.
    Demonstrates E3 conditionals, E6 enumerate(), and E4 string methods.
    """
    display_header("Recent File Tracker")
    if not files:
        print("No files loaded. Please scan a folder first (Menu option 1).")
        return

    print("Filter files modified in:")
    print("1. Today (calendar-day: since 00:00 today)")
    print("2. Last 3 days")
    print("3. Last 7 days")
    print("4. Last 30 days")
    print("5. Return to Main Menu")

    choice = input("Enter choice (1-5): ").strip()

    if choice == "1":
        label = "Today (since 00:00)"
        recent = filter_recent_files(files, mode_days=0)
    elif choice == "2":
        label = "Last 3 Days"
        recent = filter_recent_files(files, mode_days=3)
    elif choice == "3":
        label = "Last 7 Days"
        recent = filter_recent_files(files, mode_days=7)
    elif choice == "4":
        label = "Last 30 Days"
        recent = filter_recent_files(files, mode_days=30)
    elif choice == "5":
        return
    else:
        print("Invalid choice. Please select 1 to 5.")
        return

    print(f"\n{label}: {len(recent)} file(s) found")
    print("-" * 70)
    if not recent:
        print("No files were modified within this timeframe.")
        print("-" * 70)
        return

    print(f"{'#':<4} {'Filename':<30} {'Size':<12} {'Last Modified':<20}")
    print("-" * 70)
    for idx, f in enumerate(recent, start=1):
        mod_str = format_timestamp(f['modified_time'])
        try:
            from utils import get_project_path
            rel = os.path.relpath(f['path'], get_project_path())
        except Exception:
            rel = f['path']
        print(f"{idx:<4} {f['filename'][:28]:<30} {format_size(f['size']):<12} {mod_str:<20}")
        print(f"     Location: {rel}")
    print("-" * 70)
