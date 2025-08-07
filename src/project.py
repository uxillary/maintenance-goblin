"""Helpers for the experimental `.gbln` project file format."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_project(path: str | Path) -> Dict[str, Any]:
    """Load ``path`` and return its JSON content."""

    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_project(path: str | Path, data: Dict[str, Any]) -> None:
    """Persist ``data`` to ``path`` in JSON format."""

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
