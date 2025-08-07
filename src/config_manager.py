import json
import os
from typing import Any, Dict

APP_DIR = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "MaintenanceGoblin")
CONFIG_DIR = os.path.join(APP_DIR, "config")


def load_json(name: str, default: Dict[str, Any]) -> Dict[str, Any]:
    """Load ``name`` from ``CONFIG_DIR`` returning ``default`` on error."""

    path = os.path.join(CONFIG_DIR, name)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        data = default.copy()
    return data


def save_json(name: str, data: Dict[str, Any]) -> None:
    """Persist ``data`` as JSON under ``CONFIG_DIR``."""

    os.makedirs(CONFIG_DIR, exist_ok=True)
    path = os.path.join(CONFIG_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
