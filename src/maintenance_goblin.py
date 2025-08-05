"""Maintenance Goblin
=====================

A Windows maintenance utility with a playful personality. This module
contains the core logic and GUI for the Maintenance Goblin application.

It currently exposes a Tk-based interface styled with ``ttkbootstrap``.
Future versions will add a dedicated command line interface and advanced
packaging to distribute the goblin more easily.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk

import ttkbootstrap as ttkb

__all__ = [
    "__version__",
    "main",
]

# Semantic version of the application
__version__ = "0.1.0"

APP_NAME = "Maintenance Goblin"
LOG_DIR = os.path.join(os.getcwd(), "logs")


def is_admin() -> bool:
    """Return ``True`` if the current process has administrative rights."""

    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def elevate() -> None:
    """Restart the script with administrative privileges if required."""

    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


def log_message(widget: tk.Text, message: str) -> None:
    """Append ``message`` to ``widget`` and keep the widget read-only."""

    widget.configure(state="normal")
    widget.insert("end", f"{message}\n")
    widget.see("end")
    widget.configure(state="disabled")


def run_task(
    command: str,
    label: str,
    log_widget: tk.Text,
    log_file: str | None = None,
) -> None:
    """Execute ``command`` and display output in ``log_widget``.

    Parameters
    ----------
    command:
        The shell command to execute.
    label:
        Human friendly description of the command.
    log_widget:
        ``tk.Text`` widget used for displaying output.
    log_file:
        Optional file name to save the command's ``stdout`` to ``LOG_DIR``.
    """

    log_message(log_widget, f"\n▶ {label} started...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if log_file:
            os.makedirs(LOG_DIR, exist_ok=True)
            with open(os.path.join(LOG_DIR, log_file), "w", encoding="utf-8") as fh:
                fh.write(result.stdout)
        log_message(log_widget, result.stdout.strip() or "[No Output]")
        log_message(log_widget, f"✅ {label} completed.")
    except Exception as exc:  # pragma: no cover - defensive
        log_message(log_widget, f"❌ Error during {label}: {exc}")


def clear_temp(log_widget: tk.Text) -> None:
    """Remove files in the Windows temporary directory."""

    temp_path = os.environ.get("TEMP", "")
    count = 0
    for root_dir, _dirs, files in os.walk(temp_path):
        for name in files:
            try:
                os.remove(os.path.join(root_dir, name))
                count += 1
            except OSError:
                pass
    log_message(log_widget, f"🧹 Cleared {count} temp files.")


def run_all_tasks(ui: dict[str, tk.Widget]) -> None:
    """Execute the full suite of maintenance tasks."""

    def task() -> None:
        ui["status"].configure(text="Goblin working...")
        ui["progress"].start()
        ui["button"].configure(state="disabled")

        run_task(
            "sfc /scannow",
            "SFC Scan",
            ui["log"],
            "sfc_log.txt",
        )
        run_task(
            "DISM /Online /Cleanup-Image /RestoreHealth",
            "DISM Health Restore",
            ui["log"],
            "dism_log.txt",
        )
        clear_temp(ui["log"])
        run_task("cleanmgr", "Disk Cleanup", ui["log"])
        run_task(
            "defrag C: /O",
            "Drive Optimization",
            ui["log"],
            "defrag_log.txt",
        )

        ui["progress"].stop()
        ui["status"].configure(text="Goblin rests.")
        ui["button"].configure(state="normal")
        log_message(
            ui["log"],
            "\n👺 Goblin finished his chores. You may sacrifice snacks now.",
        )

    threading.Thread(target=task, daemon=True).start()


def create_gui() -> ttkb.Window:
    """Create and return the main application window."""

    root = ttkb.Window(title=APP_NAME, themename="flatly")
    root.geometry("520x480")
    root.resizable(False, False)

    ui: dict[str, tk.Widget] = {}
    ttk.Label(root, text=APP_NAME, font=("Segoe UI", 16, "bold")).pack(pady=10)

    ui["status"] = ttk.Label(root, text="Idle", foreground="gray")
    ui["status"].pack()

    ui["progress"] = ttk.Progressbar(root, mode="indeterminate")
    ui["progress"].pack(fill="x", padx=20, pady=5)

    ui["log"] = tk.Text(
        root,
        height=15,
        width=65,
        wrap="word",
        bg="#f9f9f9",
        relief="sunken",
    )
    ui["log"].pack(padx=10, pady=10)
    ui["log"].insert("end", "👺 The Maintenance Goblin is snoozing.\n")
    ui["log"].configure(state="disabled")

    ui["button"] = ttk.Button(
        root,
        text="🧼 Summon the Maintenance Goblin",
        command=lambda: run_all_tasks(ui),
        bootstyle="success",
    )
    ui["button"].pack(pady=10)

    return root


def main() -> None:
    """Entry point for running the GUI application."""

    os.makedirs(LOG_DIR, exist_ok=True)
    elevate()
    root = create_gui()
    root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    main()
