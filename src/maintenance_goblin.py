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
import random
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


# Semantic version of the application
__version__ = "0.2.0"

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

# Fun phrases displayed while tasks are running
PHRASES = [
    "Goblin rummages through bits...",
    "Goblin sharpens tiny broom...",
    "Goblin mutters incantations...",
    "Goblin dances around cache fires...",
]


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
    widget.configure(state="normal")
    widget.insert("end", f"{message}\n")
    widget.see("end")
    widget.configure(state="disabled")


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
        print(message, end="")
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


def animate_status(label: ttk.Label, stop_event: threading.Event) -> None:
    """Rotate whimsical phrases on ``label`` until ``stop_event`` is set."""

    while not stop_event.is_set():
        label.configure(text=random.choice(PHRASES))
        time.sleep(1.5)


def toggle_theme(style: ttkb.Style) -> None:
    """Switch between a light and dark theme."""

    current = style.theme_use()
    style.theme_use("flatly" if current == "darkly" else "darkly")


def get_system_info() -> dict[str, str]:
    """Return CPU, RAM and OS information."""

    return {
        "cpu": f"CPU: {psutil.cpu_percent(interval=None)}%",
        "ram": f"RAM: {psutil.virtual_memory().percent}%",
        "os": f"OS: {platform.platform()}",
    }


def update_system_info(ui: Dict[str, tk.Widget]) -> None:
    """Refresh the system information labels periodically."""

    info = get_system_info()
    ui["cpu_var"].set(info["cpu"])
    ui["ram_var"].set(info["ram"])
    # OS generally does not change, set once
    if not ui["os_var"].get():
        ui["os_var"].set(info["os"])
    ui["root"].after(2000, lambda: update_system_info(ui))


def toggle_logs(ui: Dict[str, tk.Widget]) -> None:
    """Show or hide the log tab in the notebook."""

    nb: ttk.Notebook = ui["notebook"]
    tab_id = ui["log_tab"]
    state = nb.tab(tab_id, "state")
    nb.tab(tab_id, state="hidden" if state == "normal" else "normal")


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
    txt.insert("end", notes or "No release notes")
    txt.configure(state="disabled")
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


def run_selected_tasks(ui: Dict[str, tk.Widget]) -> None:
    """Run the tasks selected in the menu."""

    selected = [t for t in TASKS if ui["task_vars"][t.label].get()]
    if not selected:
        return

    ui["run_button"].configure(state="disabled")
    ui["progress"]["maximum"] = len(selected)
    ui["progress"]["value"] = 0

    stop_event = threading.Event()
    threading.Thread(
        target=animate_status, args=(ui["status"], stop_event), daemon=True
    ).start()

    before = psutil.disk_usage("C:\\").free if not TEST_MODE else 0

    def worker() -> None:
        for task in selected:
            run_task(task, ui)
            ui["progress"]["value"] += 1
        after = psutil.disk_usage("C:\\").free if not TEST_MODE else 0
        diff = (after - before) / (1024 ** 3)
        log_message(ui["log"], f"Free space change: {diff:.2f} GiB")
        stop_event.set()
        ui["status"].configure(text="Goblin rests.")
        ui["run_button"].configure(state="normal")

    threading.Thread(target=worker, daemon=True).start()


def create_gui(root: ttkb.Window) -> None:
    """Populate ``root`` with the application's widgets."""

    style = root.style
    root.minsize(600, 400)

    ui: Dict[str, tk.Widget] = {"root": root}

    ttk.Label(root, text=APP_NAME, font=("Segoe UI", 16, "bold")).pack(pady=5)

    ui["status"] = ttk.Label(root, text="Idle", bootstyle="secondary")
    ui["status"].pack()

    ui["progress"] = ttk.Progressbar(root, mode="determinate")
    ui["progress"].pack(fill="x", padx=10, pady=5)

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True, padx=10, pady=5)
    ui["notebook"] = nb

    # System info tab
    sys_tab = ttk.Frame(nb)
    nb.add(sys_tab, text="System Info")
    cpu_var = tk.StringVar()
    ram_var = tk.StringVar()
    os_var = tk.StringVar()
    ttk.Label(sys_tab, textvariable=cpu_var).pack(anchor="w")
    ttk.Label(sys_tab, textvariable=ram_var).pack(anchor="w")
    ttk.Label(sys_tab, textvariable=os_var).pack(anchor="w")
    ui.update({"cpu_var": cpu_var, "ram_var": ram_var, "os_var": os_var})

    # Log tab
    log_tab = ttk.Frame(nb)
    nb.add(log_tab, text="Logs")
    log_widget = ScrolledText(log_tab, wrap="word")
    log_widget.pack(fill="both", expand=True)
    log_widget.insert("end", "👺 The Maintenance Goblin is snoozing.\n")
    log_widget.configure(state="disabled")
    ui["log"] = log_widget
    ui["log_tab"] = log_tab

    buttons = ttk.Frame(root)
    buttons.pack(pady=5)

    task_vars: Dict[str, tk.BooleanVar] = {}
    task_menu_btn = ttk.Menubutton(buttons, text="Tasks")
    task_menu = tk.Menu(task_menu_btn, tearoff=False)
    task_menu_btn["menu"] = task_menu
    for t in TASKS:
        var = tk.BooleanVar(value=True)
        task_menu.add_checkbutton(label=t.label, variable=var)
        task_vars[t.label] = var
    task_menu_btn.pack(side="left", padx=5)
    ui["task_vars"] = task_vars

    run_btn = ttk.Button(
        buttons, text="Run Selected", command=lambda: run_selected_tasks(ui), bootstyle="success"
    )
    run_btn.pack(side="left", padx=5)
    ui["run_button"] = run_btn

    ttk.Button(
        buttons, text="Toggle Logs", command=lambda: toggle_logs(ui)
    ).pack(side="left", padx=5)
    ttk.Button(
        buttons, text="Export Report", command=lambda: export_report(ui["log"])
    ).pack(side="left", padx=5)
    ttk.Button(
        buttons, text="Toggle Theme", command=lambda: toggle_theme(style)
    ).pack(side="left", padx=5)

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

    ttk.Checkbutton(
        buttons, text="Run at startup", variable=autostart_var, command=on_autostart
    ).pack(side="left", padx=5)
    ttk.Button(buttons, text="Gallery", command=lambda: achievements.show_gallery(root)).pack(
        side="left", padx=5
    )

    update_system_info(ui)

    def update_cb(latest: Optional[str], notes: str, url: str) -> None:
        if not latest:
            return
        root.after(0, lambda: show_update_dialog(ui, latest, notes, url))

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

    os.makedirs(APP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    if args.cli:
        if os.name == "nt" and not is_admin():
            print("Not admin. Relaunching...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
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
        if os.name == "nt" and not is_admin():
            print("Not admin. Relaunching...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
        run_tasks_silent()
        return

    if os.name == "nt" and not is_admin():
        print("Not admin. Relaunching...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

    if not SILENT_MODE:
        show_splash()

    root = ttk.Window(title=APP_NAME, themename="darkly")
    create_gui(root)
    root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    main()

