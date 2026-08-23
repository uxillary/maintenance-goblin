"""Theme cycling regression tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import maintenance_goblin as app


class FakeStyle:
    def __init__(self, theme: str) -> None:
        self.theme = theme

    def theme_use(self, theme: str | None = None) -> str:
        if theme is not None:
            self.theme = theme
        return self.theme


class ThemeTests(unittest.TestCase):
    def test_theme_cycles_through_all_three_options(self) -> None:
        style = FakeStyle("superhero")
        with patch.object(app, "configure_readability_styles"):
            sequence = [app.toggle_theme(style) for _ in range(3)]

        self.assertEqual(sequence, ["darkly", "flatly", "superhero"])

    def test_unknown_theme_returns_to_supported_cycle(self) -> None:
        style = FakeStyle("unknown")
        with patch.object(app, "configure_readability_styles"):
            selected = app.toggle_theme(style)

        self.assertEqual(selected, "superhero")


if __name__ == "__main__":
    unittest.main()
