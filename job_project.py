"""
Mini Project: Job Application Tracker
A Python CLI app to store and manage job applications.
"""

import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "applications.json")

STATUSES = ("Applied", "Interview", "Offer", "Rejected", "Withdrawn")


def load_applications():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_applications(apps):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(apps, f, indent=2, ensure_ascii=False)


def next_id(apps):
    if not apps:
        return 1
    return max(a["id"] for a in apps) + 1


def input_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty. Try again.")


def choose_status(current=None):
    print("\n  Status options:")
    for i, status in enumerate(STATUSES, 1):
        mark = " (current)" if current and status == current else ""
        print(f"    {i}. {status}{mark}")
    while True:
        choice = input("  Choose status (1-5): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(STATUSES):
            return STATUSES[int(choice) - 1]
        print("  Invalid choice. Enter a number from 1 to 5.")


def print_header():
    print("\n" + "=" * 44)
    print("       JOB APPLICATION TRACKER")
    print("=" * 44)


def print_app(app, detailed=False):
    print(f"\n  ID       : {app['id']}")
    print(f"  Company  : {app['company']}")
    print(f"  Position : {app['position']}")
    print(f"  Status   : {app['status']}")
    print(f"  Date     : {app['date']}")
    if detailed or app.get("notes"):
        print(f"  Notes    : {app.get('notes') or '-'} ")
    print("  " + "-" * 36)


def add_application(apps):
    print("\n--- Add Job Application ---")
    company = input_nonempty("  Company name: ")
    position = input_nonempty("  Position / Job title: ")
    status = choose_status()
    date = input("  Application date (YYYY-MM-DD) [today]: ").strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("  Invalid date format. Using today's date.")
            date = datetime.now().strftime("%Y-%m-%d")
    notes = input("  Notes (optional): ").strip()

    app = {
        "id": next_id(apps),
        "company": company,
        "position": position,
        "status": status,
        "date": date,
        "notes": notes,
    }
    apps.append(app)
    save_applications(apps)
    print(f"\n  Saved! Application #{app['id']} added for {company}.")


def view_all(apps):
    print("\n--- All Applications ---")
    if not apps:
        print("  No applications yet. Add one from the main menu.")
        return
    print(f"  Total: {len(apps)}")
    for app in apps:
        print_app(app)


def search_application(apps):
    print("\n--- Search Application ---")
    if not apps:
        print("  No applications to search.")
        return

    print("  Search by:")
    print("    1. Company")
    print("    2. Position")
    print("    3. Status")
    print("    4. ID")
    choice = input("  Choose (1-4): ").strip()
    query = input("  Enter search text: ").strip().lower()
    if not query:
        print("  Empty search. Cancelled.")
        return

    results = []
    for app in apps:
        if choice == "1" and query in app["company"].lower():
            results.append(app)
        elif choice == "2" and query in app["position"].lower():
            results.append(app)
        elif choice == "3" and query in app["status"].lower():
            results.append(app)
        elif choice == "4" and query == str(app["id"]):
            results.append(app)
        elif choice not in ("1", "2", "3", "4"):
            # fallback: search company + position
            if query in app["company"].lower() or query in app["position"].lower():
                results.append(app)

    if not results:
        print("  No matching applications found.")
        return

    print(f"\n  Found {len(results)} result(s):")
    for app in results:
        print_app(app, detailed=True)


def update_status(apps):
    print("\n--- Update Application Status ---")
    if not apps:
        print("  No applications to update.")
        return

    view_all(apps)
    raw = input("\n  Enter application ID to update: ").strip()
    if not raw.isdigit():
        print("  Invalid ID.")
        return

    app_id = int(raw)
    app = next((a for a in apps if a["id"] == app_id), None)
    if not app:
        print(f"  No application with ID {app_id}.")
        return

    print(f"\n  Updating: {app['company']} — {app['position']}")
    print(f"  Current status: {app['status']}")
    app["status"] = choose_status(current=app["status"])
    save_applications(apps)
    print(f"\n  Status updated to: {app['status']}")


def show_statistics(apps):
    print("\n--- Application Statistics ---")
    if not apps:
        print("  No data yet.")
        return

    total = len(apps)
    print(f"\n  Total applications : {total}")
    print("\n  By status:")
    for status in STATUSES:
        count = sum(1 for a in apps if a["status"] == status)
        pct = (count / total) * 100
        bar = "#" * count
        print(f"    {status:<12} {count:>3}  ({pct:5.1f}%)  {bar}")

    companies = {}
    for a in apps:
        companies[a["company"]] = companies.get(a["company"], 0) + 1
    top = sorted(companies.items(), key=lambda x: (-x[1], x[0].lower()))[:5]
    print("\n  Top companies (by applications):")
    for name, count in top:
        print(f"    {name}: {count}")


def sort_by_company(apps):
    print("\n--- Applications Sorted by Company ---")
    if not apps:
        print("  No applications to sort.")
        return

    sorted_apps = sorted(apps, key=lambda a: a["company"].lower())
    for app in sorted_apps:
        print_app(app)
    print(f"\n  Shown {len(sorted_apps)} application(s), A–Z by company.")


def main():
    apps = load_applications()

    while True:
        print_header()
        print("  1. Add Job Application")
        print("  2. View All Applications")
        print("  3. Search Application")
        print("  4. Update Application Status")
        print("  5. Calculate Application Statistics")
        print("  6. Sort Applications by Company")
        print("  7. Exit")
        print("=" * 44)

        choice = input("  Enter your choice (1-7): ").strip()

        if choice == "1":
            add_application(apps)
        elif choice == "2":
            view_all(apps)
        elif choice == "3":
            search_application(apps)
        elif choice == "4":
            update_status(apps)
        elif choice == "5":
            show_statistics(apps)
        elif choice == "6":
            sort_by_company(apps)
        elif choice == "7":
            print("\n  Goodbye! Your data is saved in applications.json\n")
            break
        else:
            print("\n  Invalid choice. Please enter 1–7.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
