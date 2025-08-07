"""Utilities to manage automatic start-up behaviour on Windows."""

import os
import sys

if os.name == "nt":  # pragma: no cover - Windows specific
    import winreg

APP_NAME = "Maintenance Goblin"
RUN_KEY = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"


def enable_autostart() -> None:
    """Register the application to run on user login."""

    if os.name != "nt":
        return
    path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{path}" --silent')


def disable_autostart() -> None:
    """Remove start-up registration if present."""

    if os.name != "nt":
        return
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except OSError:
        pass


def is_enabled() -> bool:
    """Return ``True`` if start-up registration exists."""

    if os.name != "nt":
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except OSError:
        return False
