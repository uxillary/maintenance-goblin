"""Maintenance Goblin
=====================

A playful Windows maintenance utility with a cheeky personality.  This
module contains the core logic and GUI for the Maintenance Goblin
application.  It now offers a more featureful interface with task
selection, system information, log exporting and a lightweight testing
mode.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import os
import platform
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Dict, Optional

import psutil
import ttkbootstrap as ttkb
from ttkbootstrap import ttk
from ttkbootstrap.scrolled import ScrolledText

import achievements
import autostart
import log_delivery
import updater
from config_manager import load_json, save_json

__all__ = ["__version__", "main"]

# When packaged with PyInstaller using the ``--windowed`` flag, ``sys.stdout``
# and ``sys.stderr`` are ``None`` because there is no attached console.  The
# :mod:`argparse` module expects these streams to be writable when displaying
# usage or error messages.  If either stream is ``None`` it will raise
# ``AttributeError`` when attempting to call ``write``.  To avoid crashing when
# the application is executed as a GUI-only program, provide dummy file objects
# that safely discard any output.
if sys.stdout is None:  # pragma: no cover - relies on PyInstaller behaviour
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:  # pragma: no cover - relies on PyInstaller behaviour
    sys.stderr = open(os.devnull, "w")


# Semantic version of the application
__version__ = "0.1.2"

APP_NAME = "Maintenance Goblin"
BASE_DIR = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))

# Resolve user-specific application directory
APP_DIR = os.path.join(
    os.getenv("APPDATA", os.path.expanduser("~")), "MaintenanceGoblin"
)
LOG_DIR = os.path.join(APP_DIR, "logs")

SETTINGS = load_json("settings.json", {"autostart": False, "remote_log": {"url": ""}})

TEST_MODE = False
DEBUG_MODE = False
SILENT_MODE = False

@dataclass
class Task:
    """Container describing an executable task."""

    label: str
    command: Optional[str] = None
    log_file: Optional[str] = None
    func: Optional[Callable[[tk.Text], None]] = None
    parser: Optional[Callable[[str], str]] = None


def is_admin() -> bool:
    """Return ``True`` if the current process has administrative rights."""

    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:  # pragma: no cover - platform specific
        return False


def log_message(widget: tk.Text, message: str) -> None:
    """Append ``message`` to ``widget`` and optionally echo to console."""

    if DEBUG_MODE:
        print(message)

    target = getattr(widget, "text", widget)
    target.configure(state="normal")
    target.insert("end", f"{message}\n")
    target.see("end")
    target.configure(state="disabled")


# ---------------------------------------------------------------------------
# Task helpers
# ---------------------------------------------------------------------------


def parse_sfc(output: str) -> str:
    """Return a short status message based on ``sfc`` output."""

    lower = output.lower()
    if "no integrity violations" in lower:
        return "SFC: No integrity violations found."
    if "successfully repaired" in lower:
        return "SFC: Corrupted files repaired."
    return "SFC: Review log for details."


def parse_dism(output: str) -> str:
    """Return a short status message based on ``dism`` output."""

    lower = output.lower()
    if "restore operation completed successfully" in lower:
        return "DISM: Restore operation completed successfully."
    return "DISM: Review log for details."


def parse_chkdsk(output: str) -> str:
    """Return a short status message based on ``chkdsk`` output."""

    lower = output.lower()
    if "found no problems" in lower or "no problems found" in lower:
        return "CHKDSK: No problems found."
    return "CHKDSK: Issues detected. Review log."


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


TASKS: list[Task] = [
    Task(
        "SFC Scan",
        "sfc /scannow",
        "sfc_log.txt",
        parser=parse_sfc,
    ),
    Task(
        "DISM Health Restore",
        "DISM /Online /Cleanup-Image /RestoreHealth",
        "dism_log.txt",
        parser=parse_dism,
    ),
    Task("Check Disk", "chkdsk C:", "chkdsk_log.txt", parser=parse_chkdsk),
    Task("Clear Temp", func=clear_temp),
    Task("Disk Cleanup", "cleanmgr"),
    Task("Drive Optimization", "defrag C: /O", "defrag_log.txt"),
]


def run_task(task: Task, ui: Dict[str, tk.Widget]) -> None:
    """Execute ``task`` and display output in the log widget."""

    log_widget: tk.Text = ui["log"]
    log_message(log_widget, f"\n▶ {task.label} started...")

    if TEST_MODE:
        # Simulated output for demonstration or tests
        time.sleep(0.2)
        fake_output = f"[Simulated output for {task.label}]"
        if task.parser:
            log_message(log_widget, task.parser(fake_output))
        else:
            log_message(log_widget, fake_output)
        log_message(log_widget, f"✅ {task.label} completed.")
        for name in achievements.record(task.label):
            log_message(log_widget, f"Achievement unlocked: {name}")
        return

    if task.func:
        task.func(log_widget)
        log_message(log_widget, f"✅ {task.label} completed.")
        for name in achievements.record(task.label):
            log_message(log_widget, f"Achievement unlocked: {name}")
        return

    try:
        result = subprocess.run(
            task.command, shell=True, capture_output=True, text=True
        )
        if task.log_file:
            os.makedirs(LOG_DIR, exist_ok=True)
            with open(
                os.path.join(LOG_DIR, task.log_file), "w", encoding="utf-8"
            ) as fh:
                fh.write(result.stdout)
        if task.parser:
            log_message(log_widget, task.parser(result.stdout))
        else:
            log_message(log_widget, result.stdout.strip() or "[No Output]")
        log_message(log_widget, f"✅ {task.label} completed.")
        for name in achievements.record(task.label):
            log_message(log_widget, f"Achievement unlocked: {name}")
    except Exception as exc:  # pragma: no cover - defensive
        log_message(log_widget, f"❌ Error during {task.label}: {exc}")


def run_tasks_silent() -> None:
    """Run all tasks sequentially without launching the GUI."""

    class DummyWidget:
        def configure(self, **_: object) -> None:
            pass

        def insert(self, *args: object, **kwargs: object) -> None:
            pass

        def see(self, *args: object, **kwargs: object) -> None:
            pass

    ui: Dict[str, tk.Widget] = {"log": DummyWidget()}
    for task in TASKS:
        run_task(task, ui)


class CLILogger:
    """Lightweight logger used for CLI mode output."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path
        if self.path:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

    def configure(self, **_: object) -> None:  # pragma: no cover - trivial
        """Compatibility shim for ``tk.Text`` widget."""

    def insert(self, _index: str, message: str) -> None:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        console_message = message.encode(encoding, errors="replace").decode(encoding)
        print(console_message, end="")
        if self.path:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(message)

    def see(self, *args: object, **kwargs: object) -> None:  # pragma: no cover - noop
        pass


def run_tasks_cli(tasks: list[Task], export_log: Optional[str] = None) -> None:
    """Run ``tasks`` in a simple command-line interface."""

    ui: Dict[str, tk.Widget] = {"log": CLILogger(export_log)}
    for task in tasks:
        run_task(task, ui)


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------


class UIThreadLogger:
    """Queue text operations so worker threads never touch Tk directly."""

    def __init__(self, events: queue.Queue, text: tk.Text) -> None:
        self.events = events
        self._text = text

    def configure(self, **kwargs: object) -> None:
        self.events.put(lambda: self._text.configure(**kwargs))

    def insert(self, index: str, message: str) -> None:
        self.events.put(lambda: self._text.insert(index, message))

    def see(self, index: str) -> None:
        self.events.put(lambda: self._text.see(index))


def post_ui(ui: Dict[str, object], callback: Callable[[], None]) -> None:
    """Schedule ``callback`` for the Tk main thread."""

    ui["events"].put(callback)  # type: ignore[union-attr]


def process_ui_events(ui: Dict[str, object]) -> None:
    """Drain queued worker updates and continue polling."""

    events: queue.Queue = ui["events"]  # type: ignore[assignment]
    try:
        while True:
            events.get_nowait()()
    except queue.Empty:
        pass
    ui["root"].after(50, lambda: process_ui_events(ui))  # type: ignore[union-attr]


def toggle_theme(style: ttkb.Style) -> None:
    """Switch between a light and dark theme."""

    current = style.theme_use()
    style.theme_use("flatly" if current == "darkly" else "darkly")


def get_system_info() -> dict[str, str]:
    """Return concise system information for the overview cards."""

    memory = psutil.virtual_memory()
    system_drive = os.environ.get("SystemDrive", "C:") + "\\"
    disk = psutil.disk_usage(system_drive)
    return {
        "cpu": f"{psutil.cpu_percent(interval=None):.0f}%",
        "cpu_detail": platform.processor() or "Processor usage",
        "ram": f"{memory.percent:.0f}%",
        "ram_detail": f"{memory.used / 1024**3:.1f} of {memory.total / 1024**3:.1f} GB used",
        "storage": f"{disk.free / 1024**3:.0f} GB free",
        "storage_detail": f"{system_drive} · {disk.total / 1024**3:.0f} GB total",
        "os": platform.platform(),
    }


def update_system_info(ui: Dict[str, tk.Widget]) -> None:
    """Refresh the system information labels periodically."""

    info = get_system_info()
    ui["cpu_var"].set(info["cpu"])
    ui["ram_var"].set(info["ram"])
    ui["storage_var"].set(info["storage"])
    ui["cpu_detail_var"].set(info["cpu_detail"])
    ui["ram_detail_var"].set(info["ram_detail"])
    ui["storage_detail_var"].set(info["storage_detail"])
    # OS generally does not change, set once
    if not ui["os_var"].get():
        ui["os_var"].set(info["os"])
    ui["root"].after(2000, lambda: update_system_info(ui))


def export_report(log_widget: tk.Text) -> None:
    """Save the full log output to a timestamped ``.txt`` file."""

    os.makedirs(LOG_DIR, exist_ok=True)
    text = log_widget.get("1.0", "end").strip()
    if not text:
        return
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(LOG_DIR, f"report_{ts}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    log_message(log_widget, f"Report exported to {path}")
    log_delivery.send_log(text)


def show_update_dialog(ui: Dict[str, tk.Widget], latest: str, notes: str, url: str) -> None:
    """Display release notes and a download link for an update."""

    win = tk.Toplevel(ui["root"])
    win.title("Update Available")
    ttk.Label(win, text=f"Version {latest} is available", font=("Segoe UI", 11, "bold")).pack(
        padx=10, pady=10
    )
    txt = ScrolledText(win, width=60, height=10)
    txt.text.insert("end", notes or "No release notes")
    txt.text.configure(state="disabled")
    txt.pack(padx=10, pady=5)
    ttk.Button(win, text="Download", command=lambda: updater.open_download(url)).pack(
        pady=5
    )


def show_splash() -> None:
    """Display a simple splash screen on startup."""
    try:
        splash = tk.Tk()
    except tk.TclError:  # pragma: no cover - headless environments
        return
    splash.overrideredirect(True)
    tk.Label(splash, text="Summoning Goblin...", padx=20, pady=20).pack()
    splash.after(1500, splash.destroy)
    splash.mainloop()


def run_selected_tasks(ui: Dict[str, object]) -> None:
    """Run selected dashboard tasks sequentially in a worker thread."""

    selected = [t for t in TASKS if ui["task_vars"][t.label].get()]
    if not selected:
        ui["status_var"].set("Select at least one maintenance task.")
        return

    ui["run_button"].configure(state="disabled")
    ui["progress"]["maximum"] = len(selected)
    ui["progress"]["value"] = 0

    ui["summary_var"].set(f"0 of {len(selected)} tasks complete")
    ui["status_var"].set("Preparing maintenance…")
    for task in TASKS:
        ui["task_status_vars"][task.label].set(
            "Queued" if task in selected else "Skipped"
        )

    before = psutil.disk_usage("C:\\").free if not TEST_MODE else 0

    def worker() -> None:
        started = time.monotonic()
        for index, task in enumerate(selected, start=1):
            post_ui(
                ui,
                lambda task=task: (
                    ui["task_status_vars"][task.label].set("Running"),
                    ui["status_var"].set(f"Running {task.label}…"),
                ),
            )
            run_task(task, ui)
            post_ui(
                ui,
                lambda task=task, index=index: (
                    ui["task_status_vars"][task.label].set("Completed"),
                    ui["progress"].configure(value=index),
                    ui["summary_var"].set(
                        f"{index} of {len(selected)} tasks complete"
                    ),
                ),
            )
        after = psutil.disk_usage("C:\\").free if not TEST_MODE else 0
        diff = (after - before) / (1024 ** 3)
        log_message(ui["log"], f"Free space change: {diff:.2f} GiB")
        elapsed = time.monotonic() - started
        post_ui(
            ui,
            lambda: (
                ui["status_var"].set("Maintenance complete — Goblin rests."),
                ui["summary_var"].set(
                    f"{len(selected)} tasks completed in {elapsed:.0f}s"
                ),
                ui["run_button"].configure(state="normal"),
            ),
        )

    threading.Thread(target=worker, daemon=True).start()


def create_gui(root: ttkb.Window) -> None:
    """Build the responsive maintenance dashboard."""

    style = root.style
    root.geometry("960x720")
    root.minsize(720, 600)
    root.rowconfigure(1, weight=1)
    root.columnconfigure(0, weight=1)

    ui: Dict[str, object] = {"root": root, "events": queue.Queue()}

    header = ttk.Frame(root, padding=(24, 18, 24, 10))
    header.grid(row=0, column=0, sticky="ew")
    header.columnconfigure(0, weight=1)
    ttk.Label(
        header, text="MAINTENANCE GOBLIN", font=("Segoe UI", 18, "bold")
    ).grid(row=0, column=0, sticky="w")
    ttk.Label(
        header,
        text="Safe, transparent Windows maintenance",
        bootstyle="secondary",
    ).grid(row=1, column=0, sticky="w", pady=(2, 0))
    ttk.Label(
        header,
        text=f"v{__version__}  ·  {'Administrator' if is_admin() else 'Standard user'}",
        bootstyle="secondary",
    ).grid(row=0, column=1, rowspan=2, sticky="e")

    nb = ttk.Notebook(root, padding=(18, 0, 18, 18))
    nb.grid(row=1, column=0, sticky="nsew")
    ui["notebook"] = nb

    overview = ttk.Frame(nb, padding=(6, 18))
    nb.add(overview, text="  Overview  ")
    overview.columnconfigure(0, weight=1)
    overview.rowconfigure(2, weight=1)

    stats = ttk.Frame(overview)
    stats.grid(row=0, column=0, sticky="ew")
    for column in range(3):
        stats.columnconfigure(column, weight=1, uniform="stats")

    cards = (
        ("CPU", "cpu_var", "cpu_detail_var", "info"),
        ("MEMORY", "ram_var", "ram_detail_var", "primary"),
        ("SYSTEM STORAGE", "storage_var", "storage_detail_var", "success"),
    )
    for column, (title, value_key, detail_key, colour) in enumerate(cards):
        value_var = tk.StringVar(value="—")
        detail_var = tk.StringVar(value="Loading…")
        ui[value_key] = value_var
        ui[detail_key] = detail_var
        card = ttk.Labelframe(stats, text=title, padding=16, bootstyle=colour)
        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=(0 if column == 0 else 6, 0),
        )
        ttk.Label(
            card, textvariable=value_var, font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")
        ttk.Label(
            card, textvariable=detail_var, bootstyle="secondary"
        ).pack(anchor="w", pady=(4, 0))

    os_var = tk.StringVar()
    ui["os_var"] = os_var
    ttk.Label(overview, textvariable=os_var, bootstyle="secondary").grid(
        row=1, column=0, sticky="w", pady=(10, 14)
    )

    maintenance = ttk.Labelframe(overview, text="MAINTENANCE PLAN", padding=14)
    maintenance.grid(row=2, column=0, sticky="nsew")
    maintenance.columnconfigure(0, weight=1)

    descriptions = {
        "SFC Scan": "Check and repair protected Windows system files",
        "DISM Health Restore": "Repair the Windows component store",
        "Check Disk": "Run a read-only filesystem diagnostic",
        "Clear Temp": "Remove available files from Windows temporary storage",
        "Disk Cleanup": "Open the built-in Windows Disk Cleanup tool",
        "Drive Optimization": "Let Windows choose the correct drive optimization",
    }
    task_vars: Dict[str, tk.BooleanVar] = {}
    task_status_vars: Dict[str, tk.StringVar] = {}

    def update_selection_summary() -> None:
        selected_count = sum(var.get() for var in task_vars.values())
        ui["summary_var"].set(f"{selected_count} tasks selected")

    for row, task in enumerate(TASKS):
        item = ttk.Frame(maintenance, padding=(8, 7))
        item.grid(row=row, column=0, sticky="ew")
        item.columnconfigure(1, weight=1)
        selected_var = tk.BooleanVar(value=True)
        status_var = tk.StringVar(value="Ready")
        task_vars[task.label] = selected_var
        task_status_vars[task.label] = status_var
        ttk.Checkbutton(
            item,
            variable=selected_var,
            command=update_selection_summary,
            bootstyle="success-round-toggle",
        ).grid(row=0, column=0, rowspan=2, padx=(0, 12))
        ttk.Label(
            item, text=task.label, font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=1, sticky="w")
        ttk.Label(
            item, text=descriptions[task.label], bootstyle="secondary"
        ).grid(row=1, column=1, sticky="w")
        ttk.Label(
            item, textvariable=status_var, bootstyle="secondary"
        ).grid(row=0, column=2, rowspan=2, sticky="e", padx=(16, 4))
    ui["task_vars"] = task_vars
    ui["task_status_vars"] = task_status_vars

    action = ttk.Frame(overview, padding=(0, 16, 0, 0))
    action.grid(row=3, column=0, sticky="ew")
    action.columnconfigure(0, weight=1)
    status_var = tk.StringVar(value="Ready for maintenance")
    summary_var = tk.StringVar(value=f"{len(TASKS)} tasks selected")
    ui["status_var"] = status_var
    ui["summary_var"] = summary_var
    ttk.Label(
        action, textvariable=status_var, font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, sticky="w")
    ttk.Label(action, textvariable=summary_var, bootstyle="secondary").grid(
        row=1, column=0, sticky="w", pady=(2, 8)
    )
    progress = ttk.Progressbar(
        action, mode="determinate", bootstyle="success-striped"
    )
    progress.grid(row=2, column=0, sticky="ew", padx=(0, 18))
    ui["progress"] = progress
    run_btn = ttk.Button(
        action,
        text="Run Maintenance",
        command=lambda: run_selected_tasks(ui),
        bootstyle="success",
        padding=(22, 12),
    )
    run_btn.grid(row=0, column=1, rowspan=3, sticky="e")
    ui["run_button"] = run_btn

    log_tab = ttk.Frame(nb)
    nb.add(log_tab, text="  Logs  ")
    log_tab.rowconfigure(1, weight=1)
    log_tab.columnconfigure(0, weight=1)
    log_header = ttk.Frame(log_tab, padding=(12, 16, 12, 8))
    log_header.grid(row=0, column=0, sticky="ew")
    log_header.columnconfigure(0, weight=1)
    ttk.Label(
        log_header, text="Maintenance log", font=("Segoe UI", 13, "bold")
    ).grid(row=0, column=0, sticky="w")
    log_widget = ScrolledText(log_tab, wrap="word")
    log_widget.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
    log_text = log_widget.text
    log_text.insert("end", "👺 The Maintenance Goblin is snoozing.\n")
    log_text.configure(state="disabled")
    ui["log"] = UIThreadLogger(ui["events"], log_text)
    ttk.Button(
        log_header,
        text="Export Report",
        command=lambda: export_report(log_text),
        bootstyle="secondary-outline",
    ).grid(row=0, column=1, sticky="e")

    settings = ttk.Frame(nb, padding=24)
    nb.add(settings, text="  Settings  ")
    settings.columnconfigure(0, weight=1)
    ttk.Label(
        settings, text="Settings", font=("Segoe UI", 16, "bold")
    ).grid(row=0, column=0, sticky="w")
    ttk.Label(
        settings,
        text="Appearance, startup behavior, and goblin extras.",
        bootstyle="secondary",
    ).grid(row=1, column=0, sticky="w", pady=(3, 20))

    appearance = ttk.Labelframe(settings, text="APPEARANCE", padding=16)
    appearance.grid(row=2, column=0, sticky="ew", pady=(0, 12))
    appearance.columnconfigure(0, weight=1)
    ttk.Label(
        appearance, text="Application theme", font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, sticky="w")
    ttk.Button(
        appearance,
        text="Toggle light / dark",
        command=lambda: toggle_theme(style),
        bootstyle="secondary-outline",
    ).grid(row=0, column=1, sticky="e")

    autostart_var = tk.BooleanVar(
        value=SETTINGS.get("autostart", False) or autostart.is_enabled()
    )

    def on_autostart() -> None:
        if autostart_var.get():
            autostart.enable_autostart()
        else:
            autostart.disable_autostart()
        SETTINGS["autostart"] = autostart_var.get()
        save_json("settings.json", SETTINGS)

    startup = ttk.Labelframe(settings, text="STARTUP", padding=16)
    startup.grid(row=3, column=0, sticky="ew", pady=(0, 12))
    startup.columnconfigure(0, weight=1)
    ttk.Label(
        startup,
        text="Run Maintenance Goblin when you sign in",
        font=("Segoe UI", 10, "bold"),
    ).grid(row=0, column=0, sticky="w")
    ttk.Checkbutton(
        startup,
        variable=autostart_var,
        command=on_autostart,
        bootstyle="success-round-toggle",
    ).grid(row=0, column=1, sticky="e")

    extras = ttk.Labelframe(settings, text="GOBLIN EXTRAS", padding=16)
    extras.grid(row=4, column=0, sticky="ew")
    extras.columnconfigure(0, weight=1)
    ttk.Label(
        extras, text="View unlocked achievements", font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, sticky="w")
    ttk.Button(
        extras,
        text="Open Gallery",
        command=lambda: achievements.show_gallery(root),
        bootstyle="secondary-outline",
    ).grid(row=0, column=1, sticky="e")

    update_system_info(ui)
    process_ui_events(ui)

    def update_cb(latest: Optional[str], notes: str, url: str) -> None:
        if not latest:
            return
        post_ui(ui, lambda: show_update_dialog(ui, latest, notes, url))

    updater.check_async(__version__, update_cb)


def main() -> None:
    """Entry point for running the GUI application."""

    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument(
        "--test", action="store_true", help="Run in test mode without making changes"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print debug logs to the console"
    )
    parser.add_argument(
        "--silent", action="store_true", help="Run all tasks without the GUI"
    )
    parser.add_argument(
        "--cli", action="store_true", help="Run in command-line mode"
    )
    parser.add_argument(
        "--run-all", action="store_true", help="Run all tasks in CLI mode"
    )
    parser.add_argument(
        "--sfc-only", action="store_true", help="Run only the SFC scan"
    )
    parser.add_argument(
        "--cleanup-only", action="store_true", help="Run cleanup tasks only"
    )
    parser.add_argument(
        "--export-log", metavar="PATH", help="Save CLI log output to PATH"
    )
    args = parser.parse_args()
    global TEST_MODE, DEBUG_MODE, SILENT_MODE
    TEST_MODE = args.test
    DEBUG_MODE = args.debug
    SILENT_MODE = args.silent

    # Simulated test runs do not invoke Windows maintenance commands and should
    # not require an administrator relaunch. Real GUI, CLI, and silent runs do.
    if os.name == "nt" and not TEST_MODE and not is_admin():
        print("Not admin. Relaunching...")
        params = subprocess.list2cmdline(
            sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv
        )
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        sys.exit()

    os.makedirs(APP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    if args.cli:
        if args.run_all or (not args.sfc_only and not args.cleanup_only):
            selected = TASKS
        elif args.sfc_only:
            selected = [t for t in TASKS if t.label == "SFC Scan"]
        elif args.cleanup_only:
            selected = [
                t
                for t in TASKS
                if t.label in {"Clear Temp", "Disk Cleanup", "Drive Optimization"}
            ]
        else:
            selected = TASKS
        run_tasks_cli(selected, args.export_log)
        return

    if SILENT_MODE:
        run_tasks_silent()
        return

    if not SILENT_MODE:
        show_splash()

    root = ttkb.Window(title=APP_NAME, themename="superhero")
    create_gui(root)
    root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    main()

