import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import shutil

import ctypes
import sys
import os

#admin priviledges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Folder for logs
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def run_command(command, log_name):
    try:
        with open(os.path.join(LOG_DIR, log_name), 'w') as f:
            subprocess.run(command, shell=True, check=True, stdout=f, stderr=subprocess.STDOUT)
        messagebox.showinfo("Success", f"{log_name} completed!")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", f"{log_name} failed!")

def sfc_scan():
    run_command("sfc /scannow", "sfc_log.txt")

def dism_restore():
    run_command("DISM /Online /Cleanup-Image /RestoreHealth", "dism_log.txt")

def clean_temp():
    temp = os.environ['TEMP']
    count = 0
    for root, dirs, files in os.walk(temp):
        for name in files:
            try:
                os.remove(os.path.join(root, name))
                count += 1
            except:
                continue
    messagebox.showinfo("Temp Cleanup", f"Deleted {count} temp files.")

def disk_cleanup():
    subprocess.run("cleanmgr", shell=True)

def defrag():
    run_command("defrag C: /O", "defrag_log.txt")

def open_logs():
    os.startfile(LOG_DIR)

# GUI Setup
root = tk.Tk()
root.title("PC Maintenance Buddy")
root.geometry("300x350")
root.resizable(False, False)

tk.Label(root, text="Pick a task:", font=("Segoe UI", 14)).pack(pady=10)

tk.Button(root, text="Run SFC Scan", command=sfc_scan).pack(pady=5)
tk.Button(root, text="Run DISM Health Restore", command=dism_restore).pack(pady=5)
tk.Button(root, text="Clear Temp Files", command=clean_temp).pack(pady=5)
tk.Button(root, text="Run Disk Cleanup", command=disk_cleanup).pack(pady=5)
tk.Button(root, text="Defrag C: Drive", command=defrag).pack(pady=5)
tk.Button(root, text="Open Logs Folder", command=open_logs).pack(pady=10)

tk.Label(root, text="Logs saved in: /logs", font=("Segoe UI", 8)).pack()

root.mainloop()
