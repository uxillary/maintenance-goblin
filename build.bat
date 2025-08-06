@echo off
REM Optional: add "--icon path\to\icon.ico" to include a custom icon
pyinstaller src\maintenance_goblin.py --onefile --windowed --name MaintenanceGoblin
