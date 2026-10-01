"""
Job Application Tracker
=======================
 
A clean, terminal-based Python app to track your job search.
Applications are saved in applications.json (created automatically
next to this file), so nothing is lost when the program closes.
 
FEATURES
    - Add, view, search, update, sort and delete job applications
    - Statistics dashboard with interview rate (division-by-zero safe)
    - Demo dashboard at startup for new users
    - Input validation: the program never crashes on bad input
 
TECHNOLOGIES
    Python 3.8+, standard library only (json, os, datetime).
    No pip install needed.
 
PYTHON CONCEPTS DEMONSTRATED
    Functions, arguments, return values, default arguments, lambda
    functions (sorting), recursion (ask_until_valid), closures
    (make_choice_validator), local/global scope, docstrings, lists,
    dictionaries, file handling, JSON, exception handling, loops.
 
HOW TO RUN
    python job_tracker.py
 
FUTURE IMPROVEMENTS
    MySQL database, Flask web app, Streamlit dashboard, login system,
    resume upload, job description matching, email reminders.
 
FILE LAYOUT (all in this one file)
    Part 1 - Utility functions (storage, validation, search, sort, stats)
    Part 2 - Main program (menu and program flow)
"""
 
import json
import os
from datetime import datetime
 
 
# =========================================================================
# PART 1: UTILITY FUNCTIONS
# =========================================================================
 
# --- Module-level (global) constants -------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "applications.json")
 
WIDTH = 60
DATE_FORMAT = "%d-%m-%Y"
MAX_RETRIES = 3
BACK_WORDS = ("b", "back")
 
JOB_TYPES = ["Full-time", "Internship", "Part-time"]
STATUSES = ["Applied", "Interview", "Rejected", "Offer"]
 
SAMPLE_APPLICATIONS = [
    {"company": "TCS", "role": "Python Developer",
     "location": "Mumbai", "status": "Applied"},
    {"company": "Infosys", "role": "Software Developer",
     "location": "Pune", "status": "Interview"},
    {"company": "Accenture", "role": "Junior Python Developer",
     "location": "Bangalore", "status": "Offer"},
]
 
 
# --- Terminal formatting ---------------------------------------------------
def print_header(title, fill="="):
    """Print a centred title padded with `fill` characters to WIDTH."""
    print(f" {title} ".center(WIDTH, fill))
 
 
def print_separator(char="-"):
    """Print a full-width horizontal line."""
    print(char * WIDTH)
 
 
def print_success(message):
    """Print a success message with a check mark."""
    print(f"\n✓ {message}")
 
 
def print_error(message):
    """Print an error message with a cross."""
    print(f"\n✗ {message}")
 
 
# --- JSON storage ----------------------------------------------------------
def save_applications(applications, filepath=DATA_FILE):
    """Write applications to a JSON file.
 
    Writes to a temporary file first and then swaps it in, so a crash
    mid-write can never leave a half-written (corrupted) data file.
 
    Returns:
        bool: True if saved successfully, False otherwise.
    """
    temp_path = filepath + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(applications, file, indent=4, ensure_ascii=False)
        os.replace(temp_path, filepath)
        return True
    except OSError as error:
        print_error(f"Could not save data: {error}")
        return False
 
 
def load_applications(filepath=DATA_FILE):
    """Load applications from JSON, creating the file if it is missing.
 
    If the file is unreadable or not a JSON list, it is renamed to
    `.corrupted` (so nothing is lost) and an empty list is returned.
 
    Returns:
        list[dict]: The saved applications.
    """
    if not os.path.exists(filepath):
        save_applications([], filepath)
        return []
 
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("Expected a list of applications.")
        return data
    except ValueError:  # json.JSONDecodeError is a subclass of ValueError
        backup_path = filepath + ".corrupted"
        os.replace(filepath, backup_path)
        print_error(f"Data file was invalid. Backed up as '{os.path.basename(backup_path)}'.")
        save_applications([], filepath)
        return []
    except OSError as error:
        print_error(f"Could not read data file: {error}")
        return []
 
 
# --- Input validation ------------------------------------------------------
def validate_text(raw):
    """Validator: accept any non-empty text. Returns (is_valid, value_or_error)."""
    if not raw:
        return False, "This field cannot be empty."
    return True, raw
 
 
def validate_date(raw):
    """Validator: accept DD-MM-YYYY. Blank input defaults to today's date."""
    if not raw:
        return True, datetime.now().strftime(DATE_FORMAT)
    try:
        datetime.strptime(raw, DATE_FORMAT)
        return True, raw
    except ValueError:
        return False, "Invalid date. Please use DD-MM-YYYY (e.g. 01-10-2026)."
 
 
def make_choice_validator(options):
    """Build a validator that accepts an option's number or its name.
 
    This is a closure: the returned function remembers `options` even
    after make_choice_validator has finished running.
    """
    def validator(raw):
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return True, options[int(raw) - 1]
        for option in options:
            if raw.lower() == option.lower():
                return True, option
        return False, f"Please choose a number between 1 and {len(options)}."
    return validator
 
 
def make_number_validator(low, high):
    """Build a validator that accepts an integer between low and high."""
    def validator(raw):
        try:
            number = int(raw)
        except ValueError:
            return False, "Please enter a valid number."
        if not low <= number <= high:
            return False, f"Please enter a number between {low} and {high}."
        return True, number
    return validator
 
 
def validate_yes_no(raw):
    """Validator: accept yes/no (or y/n). Returns a bool as the value."""
    answer = raw.lower()
    if answer in ("yes", "y"):
        return True, True
    if answer in ("no", "n"):
        return True, False
    return False, "Please type 'yes' or 'no'."
 
 
def ask_until_valid(prompt, validator, retries_left=MAX_RETRIES):
    """Ask for input until `validator` accepts it (recursive retry).
 
    Recursion fits here because each retry is the same problem with one
    fewer attempt left. The base case stops the program from nagging forever.
 
    Args:
        prompt: Text shown to the user.
        validator: Function taking the raw string, returning (ok, value_or_error).
        retries_left: Remaining attempts before giving up.
 
    Returns:
        The validated value, or None if the user typed 'back' or ran out of attempts.
    """
    if retries_left == 0:
        print_error("Too many invalid attempts. Returning to the main menu.")
        return None
 
    raw = input(prompt).strip()
    if raw.lower() in BACK_WORDS:
        return None
 
    is_valid, result = validator(raw)
    if is_valid:
        return result
 
    print_error(result)
    return ask_until_valid(prompt, validator, retries_left - 1)
 
 
def confirm(question):
    """Ask a yes/no question. Returns True only for an explicit 'yes'."""
    return bool(ask_until_valid(f"{question} (yes/no): ", validate_yes_no))
 
 
# --- Display ---------------------------------------------------------------
def format_application(application, number):
    """Return one application as a multi-line, aligned string."""
    return (
        f"#{number}\n"
        f"Company  : {application['company']}\n"
        f"Role     : {application['role']}\n"
        f"Location : {application['location']}\n"
        f"Type     : {application['job_type']}\n"
        f"Status   : {application['status']}\n"
        f"Date     : {application['date']}"
    )
 
 
def display_applications(applications, title="YOUR APPLICATIONS", numbers=None):
    """Print applications in a clean list.
 
    Args:
        applications: List of application dicts.
        title: Heading text.
        numbers: Optional list of numbers to show (used by search so each
            result keeps its real position in the full list).
    """
    print()
    print_header(title)
    if not applications:
        print("\nNo applications to show.\n")
        return
    numbers = numbers or range(1, len(applications) + 1)
    for number, application in zip(numbers, applications):
        print()
        print(format_application(application, number))
        print()
        print_separator()
 
 
def display_sample_dashboard():
    """Print the demo applications shown at startup."""
    print_header("SAMPLE APPLICATIONS", "-")
    for number, sample in enumerate(SAMPLE_APPLICATIONS, start=1):
        print(f"\n{number}. {sample['company']}")
        print(f"   Role     : {sample['role']}")
        print(f"   Location : {sample['location']}")
        print(f"   Status   : {sample['status']}")
    print()
    print_separator()
    print("\nThis is a demo view.")
    print("Your actual applications will appear here after you add them.\n")
 
 
def select_application(applications, action):
    """Show a compact numbered list and let the user pick one.
 
    Returns:
        int | None: Zero-based index of the chosen application, or None if cancelled.
    """
    print(f"\nSelect an application to {action}:\n")
    for number, app in enumerate(applications, start=1):
        print(f"{number}. {app['company']} - {app['role']} ({app['status']})")
    print("\n(Type 'back' to return to the main menu)")
    choice = ask_until_valid(
        "\nEnter number: ", make_number_validator(1, len(applications))
    )
    return None if choice is None else choice - 1
 
 
# --- Searching, sorting, statistics ----------------------------------------
def search_applications(applications, field, term):
    """Case-insensitive 'contains' search on one field.
 
    Returns:
        list[tuple[int, dict]]: (original 1-based number, application) pairs.
    """
    term = term.lower()
    return [
        (number, app)
        for number, app in enumerate(applications, start=1)
        if term in app[field].lower()
    ]
 
 
def parse_date(date_text):
    """Convert 'DD-MM-YYYY' to a datetime; bad data sorts as the oldest."""
    try:
        return datetime.strptime(date_text, DATE_FORMAT)
    except ValueError:
        return datetime.min
 
 
# Lambdas are used as sort keys because each is a tiny, one-off function.
# Writing a full `def` for every column would be noisy; a lambda keeps the
# "how do I sort by this field?" rule right next to its menu label.
SORT_OPTIONS = {
    "1": ("Company", lambda app: app["company"].lower()),
    "2": ("Role", lambda app: app["role"].lower()),
    "3": ("Location", lambda app: app["location"].lower()),
    "4": ("Status", lambda app: STATUSES.index(app["status"])),
    "5": ("Application Date", lambda app: parse_date(app["date"])),
}
 
 
def sort_applications(applications, key, reverse=False):
    """Sort the list in place using the given key function."""
    applications.sort(key=key, reverse=reverse)
 
 
def calculate_interview_rate(interviews, total):
    """Return interviews / total * 100, or 0.0 when there are no applications."""
    if total == 0:
        return 0.0
    return interviews / total * 100
 
 
def calculate_statistics(applications):
    """Count applications per status.
 
    Returns:
        dict: {'Total': n, 'Applied': n, 'Interview': n, 'Rejected': n, 'Offer': n}
    """
    stats = {"Total": len(applications)}
    for status in STATUSES:
        stats[status] = 0
    for app in applications:
        if app["status"] in stats:
            stats[app["status"]] += 1
    return stats
 
 
# =========================================================================
# PART 2: MAIN PROGRAM (menu and program flow)
# =========================================================================
 
# Global variable: counts changes made during this run.
# Functions must use the `global` keyword to modify it.
session_changes = 0
 
 
def record_change():
    """Increase the session change counter (demonstrates `global`)."""
    global session_changes
    session_changes += 1
 
 
def show_welcome():
    """Print the welcome banner."""
    print()
    print_header("JOB APPLICATION TRACKER")
    print("Track your job applications in one place.\n")
    print("Welcome! 👋\n")
 
 
def show_menu():
    """Print the main menu."""
    print("What would you like to do?\n")
    print("1. Add Job Application")
    print("2. View All Applications")
    print("3. Search Application")
    print("4. Update Application Status")
    print("5. Application Statistics")
    print("6. Sort Applications")
    print("7. Delete Application")
    print("8. Exit\n")
 
 
def add_application(applications):
    """Collect details for a new application, validate them and save."""
    print()
    print_header("ADD JOB APPLICATION")
    print("Type 'back' at any prompt to return to the main menu.\n")
 
    # (key, prompt, validator, options to list first)
    fields = [
        ("company", "Company", validate_text, None),
        ("role", "Job role", validate_text, None),
        ("location", "Location", validate_text, None),
        ("date", "Application date (DD-MM-YYYY, Enter = today)",
         validate_date, None),
        ("job_type", "Job type", make_choice_validator(JOB_TYPES),
         JOB_TYPES),
        ("status", "Status", make_choice_validator(STATUSES),
         STATUSES),
    ]
 
    application = {}
    for key, prompt, validator, options in fields:
        if options:
            print()
            for number, option in enumerate(options, start=1):
                print(f"  {number}. {option}")
        value = ask_until_valid(f"{prompt}: ", validator)
        if value is None:
            print("\nCancelled. Nothing was saved.")
            return
        application[key] = value
 
    applications.append(application)
    if save_applications(applications):
        record_change()
        print_success("Application added successfully!")
    print()
    print_separator()
 
 
def view_applications(applications):
    """Display every saved application."""
    if not applications:
        print("\nYou have no applications yet. Choose option 1 to add one.")
        return
    display_applications(applications)
 
 
def search_application(applications):
    """Search by company, role, location or status."""
    if not applications:
        print("\nYou have no applications to search yet.")
        return
 
    fields = {"1": "company", "2": "role", "3": "location", "4": "status"}
    print()
    print_header("SEARCH APPLICATION")
    print("\nSearch by:\n")
    print("1. Company")
    print("2. Role")
    print("3. Location")
    print("4. Status")
    print("5. Back to Main Menu\n")
 
    choice = input("Enter your choice: ").strip()
    if choice == "5":
        return
    if choice not in fields:
        print_error("Invalid choice.")
        return
 
    field = fields[choice]
    term = input(f"Search {field}: ").strip()
    if not term:
        print_error("Search term cannot be empty.")
        return
 
    matches = search_applications(applications, field, term)
    if not matches:
        print("\nNo matching applications found.")
        return
 
    numbers = [number for number, _ in matches]
    found = [app for _, app in matches]
    display_applications(found, f"SEARCH RESULTS ({len(found)})", numbers)
 
 
def update_status(applications):
    """Change the status of one application."""
    if not applications:
        print("\nYou have no applications to update yet.")
        return
 
    print()
    print_header("UPDATE APPLICATION STATUS")
    index = select_application(applications, "update")
    if index is None:
        return
 
    print("\nNew status:\n")
    for number, status in enumerate(STATUSES, start=1):
        print(f"{number}. {status}")
    new_status = ask_until_valid(
        "\nEnter number: ", make_choice_validator(STATUSES)
    )
    if new_status is None:
        return
 
    applications[index]["status"] = new_status
    if save_applications(applications):
        record_change()
        print_success("Application status updated successfully.")
 
 
def show_statistics(applications):
    """Display the statistics dashboard."""
    stats = calculate_statistics(applications)
    rate = calculate_interview_rate(stats["Interview"], stats["Total"])
 
    print()
    print_header("APPLICATION STATISTICS")
    print()
    print(f"Total Applications : {stats['Total']}")
    print(f"Applied            : {stats['Applied']}")
    print(f"Interview          : {stats['Interview']}")
    print(f"Offer              : {stats['Offer']}")
    print(f"Rejected           : {stats['Rejected']}")
    print(f"\nInterview Rate     : {rate:.1f}%")
    print()
    print_separator("=")
 
 
def sort_applications_menu(applications):
    """Sort applications by a chosen field and save the new order."""
    if len(applications) < 2:
        print("\nYou need at least two applications to sort.")
        return
 
    print()
    print_header("SORT APPLICATIONS")
    print("\nSort by:\n")
    for key, (label, _) in SORT_OPTIONS.items():
        print(f"{key}. {label}")
    print("6. Back to Main Menu\n")
 
    choice = input("Enter your choice: ").strip()
    if choice == "6":
        return
    if choice not in SORT_OPTIONS:
        print_error("Invalid choice.")
        return
 
    label, key_function = SORT_OPTIONS[choice]
    print("\nOrder:\n\n1. Ascending (A-Z / oldest first)")
    print("2. Descending (Z-A / newest first)")
    order = ask_until_valid("\nEnter number: ", make_number_validator(1, 2))
    if order is None:
        return
 
    sort_applications(applications, key_function, reverse=(order == 2))
    if save_applications(applications):
        record_change()
        print_success(f"Applications sorted by {label.lower()}.")
    display_applications(applications, f"SORTED BY {label.upper()}")
 
 
def delete_application(applications):
    """Delete one application after confirmation."""
    if not applications:
        print("\nYou have no applications to delete.")
        return
 
    print()
    print_header("DELETE APPLICATION")
    index = select_application(applications, "delete")
    if index is None:
        return
 
    app = applications[index]
    print(f"\nSelected: {app['company']} - {app['role']}")
    if not confirm("Are you sure you want to delete this application?"):
        print("\nDeletion cancelled.")
        return
 
    applications.pop(index)
    if save_applications(applications):
        record_change()
        print_success("Application deleted successfully.")
 
 
def show_exit_message():
    """Print a farewell with a short session summary."""
    print()
    print_separator("=")
    if session_changes:
        print(f"Changes saved this session: {session_changes}")
    print("Thank you for using Job Application Tracker. Good luck! 🍀")
    print_separator("=")
    print()
 
 
def main():
    """Program entry point: load data, show the demo, run the menu loop."""
    applications = load_applications()
 
    # Map menu choices to handler functions (functions are first-class objects).
    actions = {
        "1": add_application,
        "2": view_applications,
        "3": search_application,
        "4": update_status,
        "5": show_statistics,
        "6": sort_applications_menu,
        "7": delete_application,
    }
 
    show_welcome()
    display_sample_dashboard()
 
    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()
 
        if choice == "8":
            break
        if choice in actions:
            actions[choice](applications)
        elif choice == "":
            print_error("Please enter a number from 1 to 8.")
        else:
            print_error(f"'{choice}' is not a valid option. Choose 1-8.")
        print()
 
 
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nInterrupted. Your saved data is safe.")
    show_exit_message()
 