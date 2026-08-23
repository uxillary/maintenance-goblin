@echo off
setlocal

set ICON=%~dp0goblin.ico
set ENTRY=%~dp0src\maintenance_goblin.py
set VERFILE=%~dp0versionfile.txt
set PYTHON=%~dp0.venv\Scripts\python.exe

if not exist "%PYTHON%" set PYTHON=python

rem Clean old artifacts & spec so CLI flags are honored
rmdir /s /q build dist __pycache__ 2>nul
del /q MaintenanceGoblin.spec 2>nul

"%PYTHON%" -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "MaintenanceGoblin" ^
  --icon "%ICON%" ^
  --add-data "%ICON%;." ^
  --version-file "%VERFILE%" ^
  --noconfirm ^
  --clean ^
  "%ENTRY%"

endlocal
