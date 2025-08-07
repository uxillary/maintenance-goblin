"""Check GitHub releases to determine if an update is available."""

from __future__ import annotations

import json
import threading
import urllib.request
import webbrowser
from typing import Callable, Optional

REPO = "yourname/maintenance-goblin"


def fetch_latest_version() -> tuple[str, str, str]:
    """Return (version, notes, url) for the latest release."""

    with urllib.request.urlopen(
        f"https://api.github.com/repos/{REPO}/releases/latest", timeout=5
    ) as resp:
        data = json.load(resp)
    version = data.get("tag_name", "").lstrip("v")
    notes = data.get("body", "")
    url = data.get("html_url", "")
    return version, notes, url


def check_async(current: str, callback: Callable[[Optional[str], str, str], None]) -> None:
    """Check for updates in a background thread and invoke ``callback``."""

    def worker() -> None:
        try:  # pragma: no cover - network optional
            latest, notes, url = fetch_latest_version()
            if latest and latest != current:
                callback(latest, notes, url)
            else:
                callback(None, "", "")
        except Exception:
            callback(None, "", "")

    threading.Thread(target=worker, daemon=True).start()


def open_download(url: str) -> None:
    try:  # pragma: no cover - defensive
        webbrowser.open(url)
    except Exception:
        pass
