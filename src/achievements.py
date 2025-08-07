"""Simple local achievement tracking for Maintenance Goblin."""

from __future__ import annotations

from typing import Dict, List

try:  # pragma: no cover - optional
    import winsound
except Exception:  # pragma: no cover - platform fallback
    winsound = None  # type: ignore

from config_manager import load_json, save_json

FILE_NAME = "achievements.json"
DEFAULT_DATA: Dict[str, object] = {
    "counts": {},
    "unlocked": [],
    "sound": True,
    "total_runs": 0,
}

ACHIEVEMENT_DEFS = [
    {"id": "first_summon", "name": "\U0001f9d9\ufe0f First Summon", "check": lambda d: d["total_runs"] >= 1},
    {
        "id": "weekly_ritual",
        "name": "\U0001f4c5 Weekly Ritual Master",
        "check": lambda d: d["total_runs"] >= 7,
    },
    {
        "id": "dism_overkill",
        "name": "\U0001f480 Overkill: Ran DISM 10x",
        "check": lambda d: d["counts"].get("DISM Health Restore", 0) >= 10,
    },
]


def _load() -> Dict[str, object]:
    return load_json(FILE_NAME, DEFAULT_DATA)


def _save(data: Dict[str, object]) -> None:
    save_json(FILE_NAME, data)


def record(task_label: str) -> List[str]:
    """Record execution of ``task_label`` and return newly unlocked names."""

    data = _load()
    counts: Dict[str, int] = data.setdefault("counts", {})  # type: ignore
    counts[task_label] = counts.get(task_label, 0) + 1
    data["total_runs"] = int(data.get("total_runs", 0)) + 1
    unlocked: List[str] = list(data.get("unlocked", []))

    newly: List[str] = []
    for ach in ACHIEVEMENT_DEFS:
        if ach["id"] in unlocked:
            continue
        if ach["check"](data):  # type: ignore[arg-type]
            unlocked.append(ach["id"])
            newly.append(ach["name"])
            if data.get("sound", True) and winsound:
                try:
                    winsound.MessageBeep()  # type: ignore[attr-defined]
                except Exception:
                    pass
    data["unlocked"] = unlocked
    _save(data)
    return newly


def get_unlocked() -> List[str]:
    data = _load()
    return [a["name"] for a in ACHIEVEMENT_DEFS if a["id"] in data.get("unlocked", [])]


def toggle_sound(enable: bool) -> None:
    data = _load()
    data["sound"] = bool(enable)
    _save(data)


def show_gallery(parent=None) -> None:
    import tkinter as tk
    from tkinter import ttk

    badges = get_unlocked()
    win = tk.Toplevel(parent)
    win.title("Goblin Gallery")
    ttk.Label(win, text="Achievements", font=("Segoe UI", 12, "bold")).pack(padx=10, pady=10)
    if not badges:
        ttk.Label(win, text="No achievements yet").pack(padx=10, pady=10)
    for b in badges:
        ttk.Label(win, text=b).pack(anchor="w", padx=10)
    ttk.Button(win, text="Close", command=win.destroy).pack(pady=10)
