import tkinter as tk
from tkinter import ttk
import subprocess
import os
import threading
import ctypes
import sys

# --- Elevate as Admin ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# --- Setup ---
APP_NAME = "Maintenance Goblin"
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# --- GUI Setup ---
root = tk.Tk()
root.title(APP_NAME)
root.geometry("520x480")
root.resizable(False, False)

title = tk.Label(root, text=APP_NAME, font=("Segoe UI", 16, "bold"))
title.pack(pady=10)

status_label = tk.Label(root, text="Idle", fg="gray")
status_label.pack()

progress = ttk.Progressbar(root, mode="indeterminate")
progress.pack(fill="x", padx=20, pady=5)

log_display = tk.Text(root, height=15, width=65, wrap=tk.WORD, bg="#f9f9f9", relief="sunken")
log_display.pack(padx=10, pady=10)
log_display.insert("end", "👺 The Maintenance Goblin is snoozing.\n")
log_display.config(state="disabled")

def log_message(message):
    log_display.config(state="normal")
    log_display.insert("end", f"{message}\n")
    log_display.see("end")
    log_display.config(state="disabled")

# --- Task Command Wrapper ---
def run_task(command, label, log_file=None):
    log_message(f"\n▶ {label} started...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if log_file:
            with open(os.path.join(LOG_DIR, log_file), "w", encoding="utf-8") as f:
                f.write(result.stdout)
        log_message(result.stdout.strip() or "[No Output]")
        log_message(f"✅ {label} completed.")
    except Exception as e:
        log_message(f"❌ Error during {label}: {str(e)}")

# --- Clear Temp Files Special ---
def clear_temp():
    temp_path = os.environ['TEMP']
    count = 0
    for root_, dirs, files in os.walk(temp_path):
        for name in files:
            try:
                os.remove(os.path.join(root_, name))
                count += 1
            except:
                pass
    log_message(f"🧹 Cleared {count} temp files.")

# --- Run All Tasks ---
def run_all_tasks():
    def task():
        status_label.config(text="Goblin working...")
        progress.start()
        summon_button.config(state="disabled")

        run_task("sfc /scannow", "SFC Scan", "sfc_log.txt")
        run_task("DISM /Online /Cleanup-Image /RestoreHealth", "DISM Health Restore", "dism_log.txt")
        clear_temp()
        run_task("cleanmgr", "Disk Cleanup")
        run_task("defrag C: /O", "Drive Optimization", "defrag_log.txt")

        progress.stop()
        status_label.config(text="Goblin rests.")
        summon_button.config(state="normal")
        log_message("\n👺 Goblin finished his chores. You may sacrifice snacks now.")
    
    threading.Thread(target=task).start()

# --- One Goblin Button ---
summon_button = tk.Button(root, text="🧼 Summon the Maintenance Goblin", command=run_all_tasks, font=("Segoe UI", 12, "bold"))
summon_button.pack(pady=10)

root.mainloop()
