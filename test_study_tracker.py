import unittest
import tempfile
import csv

from pathlib import Path

from study_tracker import (
    calculate_total_minutes,
    calculate_subject_totals,
    format_duration,
    save_sessions,
    load_sessions,
)


class StudyTrackerTests(unittest.TestCase):

    def setUp(self):
        """Create sample records for each test."""

        self.sessions = [
            {"date": "2026-11-20", "subject": "Python", "minutes": 30},
            {"date": "2026-11-20", "subject": "Biology", "minutes": 45},
            {"date": "2026-11-21", "subject": "Python", "minutes": 20},
        ]

    def test_total_minutes(self):
        result = calculate_total_minutes(self.sessions)

        self.assertEqual(result, 95)

    def test_empty_sessions(self):
        result = calculate_total_minutes([])

        self.assertEqual(result, 0)

    def test_subject_totals(self):
        result = calculate_subject_totals(self.sessions)

        self.assertEqual(result["Python"], 50)
        self.assertEqual(result["Biology"], 45)

    def test_empty_subject_totals(self):
        result = calculate_subject_totals([])

        self.assertEqual(result, {})

    def test_format_duration(self):
        result = format_duration(90)

        self.assertEqual(result, "1 hours 30 minutes")

    def test_csv_save_and_load(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            csv_path = Path(temp_dir) / "test_sessions.csv"

            save_sessions(self.sessions, csv_path)

            loaded = load_sessions(csv_path)

            self.assertEqual(loaded, self.sessions)

    def test_missing_csv(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            csv_path = Path(temp_dir) / "missing.csv"

            result = load_sessions(csv_path)

            self.assertEqual(result, [])

    def test_damaged_csv(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            csv_path = Path(temp_dir) / "damaged.csv"

            with csv_path.open("w", newline="", encoding="utf-8") as file:
                file.write("wrong,header\n")
                file.write("data,data\n")

            with self.assertRaises(ValueError):
                load_sessions(csv_path)


if __name__ == "__main__":
    unittest.main()
