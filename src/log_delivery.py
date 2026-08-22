"""Optional remote log delivery integrations."""

from __future__ import annotations

import urllib.request
from typing import Optional

from config_manager import load_json

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"remote_log": {"url": ""}}


def get_settings() -> dict:
    return load_json(SETTINGS_FILE, DEFAULT_SETTINGS)


def send_log(text: str) -> None:
    """Send ``text`` to configured webhook if present."""

    settings = get_settings().get("remote_log", {})
    url: Optional[str] = settings.get("url")
    if not url:
        return
    data = text.encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "text/plain"})
    try:  # pragma: no cover - network optional
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass
