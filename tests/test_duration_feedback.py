"""Duration display and task guidance tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import maintenance_goblin as app


class DurationFeedbackTests(unittest.TestCase):
    def test_format_duration(self) -> None:
        cases = {
            0: "0s",
            42.9: "42s",
            374: "6m 14s",
            3780: "1h 03m",
            -5: "0s",
        }
        for seconds, expected in cases.items():
            with self.subTest(seconds=seconds):
                self.assertEqual(app.format_duration(seconds), expected)

    def test_every_task_has_duration_guidance(self) -> None:
        self.assertEqual(
            {task.label for task in app.TASKS},
            set(app.TASK_DURATION_GUIDANCE),
        )
        self.assertEqual(set(app.TASK_DURATION_GUIDANCE), set(app.TASK_READY_GUIDANCE))

    def test_estimated_total_duration(self) -> None:
        self.assertEqual(app.estimate_total_duration([]), "—")
        self.assertEqual(
            app.estimate_total_duration([task.label for task in app.TASKS]),
            "roughly 15–40+ min",
        )
        self.assertEqual(
            app.estimate_total_duration(["SFC Scan", "Check Disk"]),
            "roughly 6–25 min",
        )
        self.assertEqual(
            app.estimate_total_duration(["Disk Cleanup"]),
            "varies; may wait for Windows",
        )


if __name__ == "__main__":
    unittest.main()
