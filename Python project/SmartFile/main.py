"""
SmartFile — Automatic File & Notes Organizer
Main Entry Point and Interactive CLI
Configured for automatic demo workflow with test_files/ and organized_files/.
"""

import sys
import os
from scanner import scan_folder
from organizer import organize_files, reset_organized_folder
from search import search_files
from duplicate_detector import find_duplicates
from renamer import rename_file
from recent_files import view_recent_files
from analyzer import analyze_folder
from reporter import save_inventory_and_report, view_history
from rules_manager import manage_rules, load_rules
from utils import display_header, get_project_path, prompt_yes_no

DEFAULT_INPUT_DIR = get_project_path("test_files")
DEFAULT_OUTPUT_DIR = get_project_path("organized_files")

def print_menu(current_folder, file_count):
    """
    Displays the main interactive menu with the current active folder status.
    Demonstrates string methods, repetition, and clean CLI layout.
    """
    print("\n" + "=" * 50)
    print("      SMARTFILE — AUTOMATIC FILE & NOTES ORGANIZER")
    print("=" * 50)
    if current_folder:
        try:
            rel = os.path.relpath(current_folder, get_project_path())
        except ValueError:
            rel = current_folder
        print(f"Active Folder: {rel}/ ({file_count} files loaded)")
    else:
        print("Active Folder: [No folder scanned yet]")
    print(f"Output Folder: organized_files/")
    print("-" * 50)
    print("1.  Scan Files")
    print("2.  Organize Files")
    print("3.  Search Files")
    print("4.  Detect Duplicate Files")
    print("5.  Rename File")
    print("6.  View Recent Files")
    print("7.  Analyze Folder")
    print("8.  Generate Reports")
    print("9.  Manage Organization Rules")
    print("10. View Organization History")
    print("11. Exit")
    print("=" * 50)

def main():
    # Automatically ensure default demo directories exist
    os.makedirs(DEFAULT_INPUT_DIR, exist_ok=True)
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

    # Automatically load test_files/ as the default active folder on launch
    current_folder = DEFAULT_INPUT_DIR
    _, initial_files = scan_folder(current_folder, verbose=False)
    files = initial_files if initial_files is not None else []

    last_analysis = {}
    last_duplicates = None

    # Load initial rules to ensure data/rules.csv exists
    load_rules()

    print("\nWelcome to SmartFile Organizer!")
    print("Demo environment initialized with 'test_files/' (Input) and 'organized_files/' (Output).")

    while True:
        print_menu(current_folder, len(files))
        choice = input("Enter choice (1-11): ").strip()

        if choice == "1":
            folder, new_files = scan_folder()
            if folder and new_files is not None:
                current_folder = folder
                files = new_files
                last_analysis = {}
                last_duplicates = None

        elif choice == "2":
            if not files:
                print("\n[Notice] No files to organize. Please scan files first (Option 1).")
                continue
            
            # If organized_files already contains files, offer option to organize or reset
            org_has_files = os.path.exists(DEFAULT_OUTPUT_DIR) and len(os.listdir(DEFAULT_OUTPUT_DIR)) > 0
            if org_has_files:
                print("\nOrganize Options:")
                print("1. Organize / Copy files into organized_files/")
                print("2. Reset organized_files/ (clear output for fresh demo)")
                print("3. Return to Main Menu")
                sub = input("Select option (1-3): ").strip()
                if sub == "1":
                    organize_files(files, DEFAULT_OUTPUT_DIR)
                elif sub == "2":
                    reset_organized_folder(DEFAULT_OUTPUT_DIR, confirm=True)
                elif sub == "3":
                    continue
                else:
                    print("Invalid option; returning to menu.")
            else:
                organize_files(files, DEFAULT_OUTPUT_DIR)

        elif choice == "3":
            search_files(files)

        elif choice == "4":
            if not files:
                print("\n[Notice] No files loaded. Please scan files first (Option 1).")
                continue
            last_duplicates = find_duplicates(files)

        elif choice == "5":
            if not files:
                print("\n[Notice] No files loaded. Please scan files first (Option 1).")
                continue
            if rename_file(files):
                # Refresh file listing
                _, refreshed = scan_folder(current_folder, verbose=False)
                if refreshed is not None:
                    files = refreshed
                    last_analysis = {}
                    last_duplicates = None

        elif choice == "6":
            if not files:
                print("\n[Notice] No files loaded. Please scan files first (Option 1).")
                continue
            view_recent_files(files)

        elif choice == "7":
            if not files:
                print("\n[Notice] No files loaded. Please scan files first (Option 1).")
                continue
            last_analysis = analyze_folder(files, show_display=True, interactive=True)

        elif choice == "8":
            if not files:
                print("\n[Notice] No files loaded. Please scan files first (Option 1).")
                continue
            if not last_analysis:
                last_analysis = analyze_folder(files, show_display=False, interactive=False)
            save_inventory_and_report(current_folder, files, last_analysis, last_duplicates)

        elif choice == "9":
            manage_rules()

        elif choice == "10":
            view_history()

        elif choice == "11":
            print("\nThank you for using SmartFile Organizer. Goodbye!")
            sys.exit(0)

        else:
            print("\n[Error] Invalid option. Please enter a valid choice between 1 and 11.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user. Exiting SmartFile.")
        sys.exit(0)
