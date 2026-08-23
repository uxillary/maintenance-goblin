"""Startup mode regression tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import maintenance_goblin as app


class StartupTests(unittest.TestCase):
    def test_window_icon_uses_bundled_icon(self) -> None:
        window = MagicMock()
        with patch.object(app.os.path, "isfile", return_value=True):
            app.set_window_icon(window)

        window.iconbitmap.assert_called_once_with(app.ICON_PATH)

    def test_missing_window_icon_is_non_fatal(self) -> None:
        window = MagicMock()
        with patch.object(app.os.path, "isfile", return_value=False):
            app.set_window_icon(window)

        window.iconbitmap.assert_not_called()

    def test_test_mode_skips_splash_and_opens_dashboard(self) -> None:
        root = MagicMock()
        with (
            patch.object(sys, "argv", ["maintenance_goblin.py", "--test"]),
            patch.object(app, "show_splash") as show_splash,
            patch.object(app.ttkb, "Window", return_value=root),
            patch.object(app, "create_gui") as create_gui,
            patch.object(app.os, "makedirs"),
        ):
            app.main()

        show_splash.assert_not_called()
        root.iconbitmap.assert_called_once_with(app.ICON_PATH)
        create_gui.assert_called_once_with(root)
        root.mainloop.assert_called_once_with()

    def test_ctrl_c_closes_console_launched_gui_cleanly(self) -> None:
        root = MagicMock()
        root.mainloop.side_effect = KeyboardInterrupt
        with (
            patch.object(sys, "argv", ["maintenance_goblin.py", "--test"]),
            patch.object(app.ttkb, "Window", return_value=root),
            patch.object(app, "create_gui"),
            patch.object(app.os, "makedirs"),
        ):
            app.main()

        root.destroy.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
