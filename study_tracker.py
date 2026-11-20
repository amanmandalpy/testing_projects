"""


Features:
- Add study sessions
- View session history
- Subject-wise summaries
- CSV persistence
- Input validation
- Exception handling
"""

import csv
from datetime import date
from pathlib import Path
from collections import defaultdict
import os
import tempfile

# ==========================================
#  PROJECT CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parent
CSV_FILE = PROJECT_DIR / "study_sessions.csv"

FIELDNAMES = ["date", "subject", "minutes"]

SUBJECTS = [
    "Python",
    "Django",
    "Linux",
    "AWS",
    "PostgreSQL",
    "Django REST Framework",
    "Ansible",
    "Docker & CI/CD",
    "English Speaking",
]


# ==========================================
# INPUT VALIDATION FUNCTIONS
# ==========================================


def get_subject():
    """Ask for a non-empty subject."""
    print("Suggested subjects:", ", ".join(SUBJECTS))
    while True:
        subject = input("Enter subject: ").strip()

        if subject:
            return subject

        print("Error: Subject cannot be empty.")


def get_minutes():
    """Accept only positive whole numbers."""

    while True:
        user_input = input("Enter study minutes: ").strip()

        try:
            minutes = int(user_input)

            if minutes <= 0:
                print("Error: Minutes must be greater than zero.")
                continue

            return minutes

        except ValueError:
            print("Error: Enter a valid whole number.")


def get_session_date():
    """Accept YYYY-MM-DD or use today's date."""

    while True:
        user_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()

        if not user_input:
            return date.today().isoformat()

        try:
            parsed_date = date.fromisoformat(user_input)

            if parsed_date.isoformat() != user_input:
                raise ValueError

            return parsed_date.isoformat()

        except ValueError:
            print("Error: Enter a real date in YYYY-MM-DD format.")


# ==========================================
#  CSV FILE HANDLING
# ==========================================


def load_sessions(file_path=CSV_FILE):
    """
    Load existing records from CSV.

    Missing file = empty history.
    Damaged file = raise an error.
    """

    if not file_path.exists():
        return []

    sessions = []

    try:
        with file_path.open(mode="r", newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            if reader.fieldnames != FIELDNAMES:
                raise ValueError("CSV header is invalid.")

            for row_number, row in enumerate(reader, start=2):

                if None in row:
                    raise ValueError(f"Extra CSV columns at row {row_number}.")

                session_date = row["date"]
                subject = row["subject"]
                minutes_text = row["minutes"]

                try:
                    parsed_date = date.fromisoformat(session_date)
                    minutes = int(minutes_text)

                    if parsed_date.isoformat() != session_date:
                        raise ValueError("Invalid date format.")

                    if not subject or not subject.strip():
                        raise ValueError("Empty subject.")

                    if minutes <= 0:
                        raise ValueError("Invalid minutes.")

                except (ValueError, TypeError) as error:
                    raise ValueError(
                        f"Invalid data at CSV row {row_number}: {error}"
                    ) from error

                sessions.append(
                    {
                        "date": session_date,
                        "subject": subject.strip(),
                        "minutes": minutes,
                    }
                )

        return sessions

    except (OSError, csv.Error, UnicodeError) as error:
        raise RuntimeError(f"Could not read CSV file: {error}") from error


def save_sessions(sessions, file_path=CSV_FILE):
    """
    Save records safely.

    Write to a temporary file first, then replace the CSV.
    This helps preserve existing records if saving fails.
    """

    file_path = Path(file_path)
    temp_path = None

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=file_path.parent,
            suffix=".tmp",
            delete=False,
        ) as temp_file:

            temp_path = Path(temp_file.name)

            writer = csv.DictWriter(temp_file, fieldnames=FIELDNAMES)

            writer.writeheader()
            writer.writerows(sessions)

            temp_file.flush()
            os.fsync(temp_file.fileno())

        os.replace(temp_path, file_path)

    except (OSError, csv.Error) as error:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

        raise RuntimeError(f"Could not save study records: {error}") from error


# ==========================================
#  STUDY CALCULATION FUNCTIONS
# ==========================================


def calculate_total_minutes(sessions):
    """Calculate total study minutes."""

    total = 0

    for session in sessions:
        total += session["minutes"]

    return total


def calculate_subject_totals(sessions):
    """Calculate study time for every subject."""

    totals = defaultdict(int)

    for session in sessions:
        subject = session["subject"]
        minutes = session["minutes"]

        totals[subject] += minutes

    return dict(totals)


def format_duration(minutes):
    """Convert minutes into hours and minutes."""

    hours = minutes // 60
    remaining_minutes = minutes % 60

    return f"{hours} hours {remaining_minutes} minutes"


# ==========================================
# ADD NEW STUDY SESSION
# ==========================================


def add_session(sessions):
    """Collect, validate and save a new session."""

    print("\n========== ADD STUDY SESSION ==========")

    session_date = get_session_date()
    subject = get_subject()
    minutes = get_minutes()

    new_session = {
        "date": session_date,
        "subject": subject,
        "minutes": minutes,
    }

    updated_sessions = sessions + [new_session]

    try:
        save_sessions(updated_sessions)

        sessions.append(new_session)

        print("\nSession saved successfully!")
        print(f"Subject: {subject}")
        print(f"Duration: {minutes} minutes")
        print(f"Date: {session_date}")

    except RuntimeError as error:
        print(f"\nSave failed: {error}")

    return sessions


# ==========================================
# DISPLAY SESSION HISTORY
# ==========================================


def view_sessions(sessions):
    """Display all saved sessions."""

    print("\n========== STUDY HISTORY ==========")

    if not sessions:
        print("No study records found.")
        return

    print(f"{'No.':<5} {'Date':<13} " f"{'Subject':<25} {'Minutes':>8}")

    print("-" * 55)

    for index, session in enumerate(sessions, start=1):

        print(
            f"{index:<5} "
            f"{session['date']:<13} "
            f"{session['subject']:<25} "
            f"{session['minutes']:>8}"
        )

    total = calculate_total_minutes(sessions)

    print("-" * 55)
    print(f"Total study time: {format_duration(total)}")


# ==========================================
# SUBJECT-WISE SUMMARY
# ==========================================


def show_summary(sessions):
    """Display subject-wise study statistics."""

    print("\n========== SUBJECT SUMMARY ==========")

    if not sessions:
        print("No study records available.")
        return

    totals = calculate_subject_totals(sessions)
    grand_total = calculate_total_minutes(sessions)

    for subject, minutes in sorted(totals.items()):

        percentage = (minutes / grand_total) * 100

        print(f"{subject:<25} " f"{format_duration(minutes):<22} " f"{percentage:.1f}%")

    print("-" * 65)
    print(f"Total: {format_duration(grand_total)}")


# ==========================================
#  DISPLAY MAIN MENU
# ==========================================


def display_menu():
    """Show application menu."""

    print("\n" + "=" * 45)
    print("       STUDY SESSION TRACKER")
    print("=" * 45)

    print("1. Add Study Session")
    print("2. View Study History")
    print("3. Subject-wise Summary")
    print("4. Show Total Study Time")
    print("5. Exit")

    print("=" * 45)


# ==========================================
# MAIN APPLICATION
# ==========================================


def main():
    """Run the application."""

    print("\nWelcome to Study Session Tracker!")

    try:
        sessions = load_sessions()

    except (RuntimeError, ValueError) as error:
        print(f"\nStartup error: {error}")
        print("Existing records have not been overwritten.")
        return

    print(f"Loaded {len(sessions)} study sessions.")

    while True:

        display_menu()

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":

            sessions = add_session(sessions)

        elif choice == "2":

            view_sessions(sessions)

        elif choice == "3":

            show_summary(sessions)

        elif choice == "4":

            total = calculate_total_minutes(sessions)

            print(f"\nTotal study time: {format_duration(total)}")

        elif choice == "5":

            print("\nThank you for using Study Session Tracker!")
            print("Keep learning and stay consistent.")
            break

        else:

            print("Invalid choice. Please select 1 to 5.")


# ==========================================
#  PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
