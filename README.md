# Maintenance Goblin

Maintenance Goblin is a friendly Windows 10/11 desktop utility for running legitimate built-in maintenance tools from one clear dashboard. It favors transparent, conservative system maintenance over misleading “PC optimizer” claims.

## Features

- Responsive Overview dashboard with live CPU, memory, and storage statistics
- Selectable maintenance plan with per-task status and overall progress
- SFC, DISM, and read-only CHKDSK maintenance
- Temporary-file cleanup that skips locked files
- Windows Disk Cleanup and drive-aware Windows optimization
- Separate in-app Logs view with report export
- Light and dark themes, startup preference, and Gallery under Settings
- Administrator elevation for real maintenance; safe `--test` mode without elevation

## Run from source

Requires Python 3.9 or newer on Windows.

```powershell
if (-not (Test-Path .\.venv\Scripts\python.exe)) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\src\maintenance_goblin.py --test
```

Run these commands from the repository folder. The first command preserves an
existing virtual environment instead of rebuilding it. Activation is optional
because every command calls the environment's Python executable directly. If
environment creation is needed, allow it to finish rather than pressing Ctrl+C.

The `--test` flag simulates tasks without running Windows maintenance commands. To perform real maintenance, omit `--test`; Windows will request administrator permission.

This command opens the desktop app and keeps running until you close its window. Pressing Ctrl+C from PowerShell also closes a console-launched test run cleanly.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Build the Windows executable

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\build.bat
```

The executable is written to `dist\MaintenanceGoblin.exe` with the project icon and Windows version metadata.

## Project information

- [Documentation](docs/index.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

Maintenance Goblin is licensed under the [MIT License](LICENSE).
