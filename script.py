import tkinter as tk
from tkinter import ttk
import subprocess
import os
import threading
import ctypes
import sys

# --- Auto-Elevate (Run as Admin) ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# --- GUI Setup ---
root = tk.Tk()
root.title("🧼 PC Maintenance Buddy")
root.geometry("520x480")
root.resizable(False, False)

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# --- Widgets ---
title = tk.Label(root, text="PC Maintenance Buddy", font=("Segoe UI", 16, "bold"))
title.pack(pady=10)

status_label = tk.Label(root, text="Idle", fg="gray")
status_label.pack()

progress = ttk.Progressbar(root, mode="indeterminate")
progress.pack(fill="x", padx=20, pady=5)

log_display = tk.Text(root, height=15, width=65, wrap=tk.WORD, bg="#f9f9f9", relief="sunken")
log_display.pack(padx=10, pady=10)
log_display.insert("end", "🧽 Ready to clean house.\n")
log_display.config(state="disabled")

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

def log_message(message):
    log_display.config(state="normal")
    log_display.insert("end", f"{message}\n")
    log_display.see("end")
    log_display.config(state="disabled")

def run_command(command, label, log_file=None):
    def task():
        status_label.config(text=f"{label} running...")
        progress.start()
        for btn in buttons:
            btn.config(state="disabled")
        log_message(f"\n▶ {label} started...")

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if log_file:
                with open(os.path.join(LOG_DIR, log_file), "w", encoding="utf-8") as f:
                    f.write(result.stdout)
            log_message(result.stdout.strip() or "[No Output]")
            log_message(f"✅ {label} completed.")
        except Exception as e:
            log_message(f"❌ Error: {str(e)}")
        finally:
            progress.stop()
            status_label.config(text="Idle")
            for btn in buttons:
                btn.config(state="normal")

    threading.Thread(target=task).start()

# --- Task Functions ---
def sfc_scan():
    run_command("sfc /scannow", "SFC Scan", "sfc_log.txt")

def dism_restore():
    run_command("DISM /Online /Cleanup-Image /RestoreHealth", "DISM Health Restore", "dism_log.txt")

def clear_temp():
    def task():
        status_label.config(text="Clearing Temp Files...")
        progress.start()
        for btn in buttons:
            btn.config(state="disabled")
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
        status_label.config(text="Idle")
        progress.stop()
        for btn in buttons:
            btn.config(state="normal")
    threading.Thread(target=task).start()

def disk_cleanup():
    run_command("cleanmgr", "Disk Cleanup")

def defrag_drive():
    run_command("defrag C: /O", "Drive Optimization", "defrag_log.txt")

# --- Buttons ---
buttons = []
btn_texts = [
    ("Run SFC Scan", sfc_scan),
    ("Run DISM Health Restore", dism_restore),
    ("Clear Temp Files", clear_temp),
    ("Run Disk Cleanup", disk_cleanup),
    ("Defrag C: Drive", defrag_drive)
]

for txt, cmd in btn_texts:
    b = tk.Button(button_frame, text=txt, width=35, command=cmd)
    b.pack(pady=3)
    buttons.append(b)

# --- Run App ---
root.mainloop()
