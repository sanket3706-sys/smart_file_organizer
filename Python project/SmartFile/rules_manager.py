"""
SmartFile Rules Manager Module
Loads, validates, adds, removes, and saves file organization rules from/to CSV.
Prevents corruption, duplicate rules, and empty keywords.
Demonstrates E3, E4, E6, E7, E10.
"""

import csv
import os
from utils import display_header, ensure_dir, get_project_path, prompt_yes_no, clean_category_name

RULES_FILE = get_project_path("data", "rules.csv")

DEFAULT_RULES = [
    {"keyword": "dsa", "category": "DSA", "subcategory": ""},
    {"keyword": "dbms", "category": "DBMS", "subcategory": ""},
    {"keyword": "physics", "category": "Physics", "subcategory": ""},
    {"keyword": "math", "category": "Mathematics", "subcategory": ""},
    {"keyword": "python", "category": "Python", "subcategory": ""},
    {"keyword": "assignment", "category": "", "subcategory": "Assignments"},
    {"keyword": "notes", "category": "", "subcategory": "Notes"},
    {"keyword": "lab", "category": "", "subcategory": "Lab"},
    {"keyword": "project", "category": "", "subcategory": "Projects"},
    {"keyword": "presentation", "category": "", "subcategory": "Presentations"}
]

def init_rules():
    """
    Ensures data directory and rules.csv exist with default rules.
    """
    ensure_dir(get_project_path("data"))
    if not os.path.exists(RULES_FILE):
        try:
            save_rules(DEFAULT_RULES)
        except (PermissionError, OSError) as e:
            print(f"Error initializing rules file: {e}")

def load_rules():
    """
    Loads organization rules from CSV with specific exception handling.
    Returns a list of rule dictionaries: [{"keyword": ..., "category": ..., "subcategory": ...}, ...]
    Demonstrates file handling, CSV DictReader, and list comprehension/appending.
    """
    init_rules()
    rules = []
    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean whitespace using string methods
                kw = row.get("keyword", "").strip()
                cat = row.get("category", "").strip()
                subcat = row.get("subcategory", "").strip()
                if kw:
                    rules.append({"keyword": kw, "category": cat, "subcategory": subcat})
    except FileNotFoundError:
        print("Notice: Rules file not found. Initializing with default rules.")
        return [dict(r) for r in DEFAULT_RULES]
    except (PermissionError, csv.Error, OSError) as e:
        print(f"Warning: Could not read rules file ({e}). Falling back to default rules.")
        return [dict(r) for r in DEFAULT_RULES]

    return rules

def save_rules(rules):
    """
    Saves the list of rule dictionaries to the rules.csv file safely.
    Demonstrates CSV DictWriter and specific exception handling.
    """
    ensure_dir(get_project_path("data"))
    try:
        with open(RULES_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["keyword", "category", "subcategory"])
            writer.writeheader()
            for r in rules:
                writer.writerow({
                    "keyword": r.get("keyword", "").strip().lower(),
                    "category": r.get("category", "").strip(),
                    "subcategory": r.get("subcategory", "").strip()
                })
        return True
    except (PermissionError, csv.Error, OSError) as e:
        print(f"Error saving rules file: {e}")
        return False

def display_rules(rules):
    """
    Displays the current rules in a formatted table using enumerate().
    Demonstrates E6 enumerate().
    """
    print("\nCURRENT ORGANIZATION RULES:")
    print("-" * 55)
    print(f"{'#':<4} {'Keyword':<16} {'Category':<16} {'Subcategory':<16}")
    print("-" * 55)
    for idx, r in enumerate(rules, start=1):
        kw = r.get('keyword', '')
        cat = r.get('category', '') or '-'
        subcat = r.get('subcategory', '') or '-'
        print(f"{idx:<4} {kw:<16} {cat:<16} {subcat:<16}")
    print("-" * 55)

def manage_rules():
    """
    Interactive rules management interface:
    View, Add, Remove, and Reset rules.
    Demonstrates E4 string methods, E5 while loop with break/continue, E10 try/except.
    """
    while True:
        display_header("Manage Organization Rules")
        print("1. View Current Rules")
        print("2. Add New Rule")
        print("3. Remove a Rule")
        print("4. Reset to Default Rules")
        print("5. Return to Main Menu")

        choice = input("Enter choice (1-5): ").strip()
        rules = load_rules()

        if choice == "1":
            display_rules(rules)

        elif choice == "2":
            kw = input("Enter keyword (e.g. 'os', 'exam'): ").strip().lower()
            if not kw:
                print("Error: Keyword cannot be empty.")
                continue

            # Check for commas which could malform CSV fields
            if ',' in kw:
                print("Error: Keyword cannot contain comma character.")
                continue

            # Check if keyword already exists using list comprehension and membership 'in'
            existing_keywords = [r['keyword'].lower() for r in rules]
            if kw in existing_keywords:
                print(f"Error: A rule with keyword '{kw}' already exists.")
                continue

            cat_raw = input("Enter Category (e.g. 'Operating Systems' or leave blank): ")
            subcat_raw = input("Enter Subcategory (e.g. 'Exams' or leave blank): ")

            cat = clean_category_name(cat_raw)
            subcat = clean_category_name(subcat_raw)

            if not cat and not subcat:
                print("Error: You must specify at least a Category or a Subcategory.")
                continue

            rules.append({"keyword": kw, "category": cat, "subcategory": subcat})
            if save_rules(rules):
                print(f"Success! Rule for '{kw}' added and saved.")

        elif choice == "3":
            display_rules(rules)
            try:
                raw_idx = input("Enter the rule number (#) to remove (or 0 to cancel): ").strip()
                if not raw_idx.isdigit():
                    print("Error: Please enter positive numeric digits only.")
                    continue

                idx = int(raw_idx)
                if idx == 0:
                    print("Removal cancelled.")
                    continue
                if 1 <= idx <= len(rules):
                    removed = rules.pop(idx - 1)
                    if save_rules(rules):
                        print(f"Success: Removed rule for '{removed['keyword']}'.")
                else:
                    print(f"Invalid rule number: please enter between 1 and {len(rules)}.")
            except ValueError:
                print("Invalid input: numeric value expected.")

        elif choice == "4":
            if prompt_yes_no("Are you sure you want to reset all rules to default?"):
                if save_rules(DEFAULT_RULES):
                    print("Rules successfully reset to factory defaults.")

        elif choice == "5":
            break
        else:
            print("Invalid choice. Please select 1 to 5.")
