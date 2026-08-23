# Maintenance Goblin — Project Context

## Product

Maintenance Goblin is a lightweight Windows 10/11 desktop maintenance utility written in Python. It provides a friendly dashboard around legitimate Windows tools while favouring safety, transparency, and conservative defaults over “PC optimizer” claims.

- Current version: `0.2.0`
- Entry point: `src/maintenance_goblin.py`
- Release artifact: `MaintenanceGoblin.exe`

The visual identity is approachable and slightly playful, but system operations, warnings, and errors must remain accurate and professional.

## Current implementation

The application currently provides:

- A responsive Overview dashboard with live CPU, memory, system-drive, OS, version, and elevation information
- Six individually selectable maintenance tasks executed sequentially in a worker thread
- Per-task queued, running, completed, and skipped states
- Current-task and session timers, approximate duration guidance, indeterminate task activity, and determinate overall progress
- A Logs view with live command output and timestamped text-report export
- A Settings view with three themes, launch-at-sign-in control, and the local achievement Gallery
- Administrator relaunch for real GUI, CLI, and silent maintenance
- A safe `--test` mode that simulates tasks without elevation or system changes
- Source-oriented CLI and silent modes with task filters and optional log export
- Local configuration, achievements, task logs, and reports under `%APPDATA%\MaintenanceGoblin`

Tk widget updates from maintenance workers are routed through a queue and processed on the main UI thread.

## Maintenance tasks

| Dashboard label | Current operation | Behaviour |
| --- | --- | --- |
| SFC Scan | `sfc /scannow` | Checks and repairs protected Windows system files. |
| DISM Health Restore | `DISM /Online /Cleanup-Image /RestoreHealth` | Repairs the Windows component store. |
| Check Disk | `chkdsk C:` | Read-only system-drive diagnostic; no `/f`, `/r`, or `/x`. |
| Clear Temp | Deletes available files below `%TEMP%` | Skips files that are locked or inaccessible. |
| Disk Cleanup | `cleanmgr` | Opens the built-in Windows Disk Cleanup tool. |
| Drive Optimization | `defrag C: /O` | Lets Windows select the appropriate optimization for the media type. |

The current commands target `C:` for CHKDSK and drive optimization. Documentation must not describe arbitrary-drive selection until it is implemented.

## Data and network behaviour

Settings and achievements are stored in `%APPDATA%\MaintenanceGoblin\config`. Task logs and exported reports are stored in `%APPDATA%\MaintenanceGoblin\logs`.

The codebase contains an asynchronous GitHub release checker, but its repository identifier is still a placeholder. Treat update checking as unfinished and do not advertise it as working. A legacy remote-log delivery helper also exists but has no user-facing configuration; do not present remote log delivery as a product feature.

The released app should otherwise be described as having no telemetry or advertising.

## Packaging and releases

`build.bat` uses PyInstaller to create a one-file, windowed `dist\MaintenanceGoblin.exe` with `goblin.ico` and metadata from `versionfile.txt`.

`installer.nsi` can build `MaintenanceGoblinSetup.exe` after the standalone executable exists, but the installer is not built or published by the current GitHub Actions workflow.

Pushing a `v*` tag triggers `.github/workflows/release.yml`, which:

1. Runs the unit tests on Windows.
2. Builds `MaintenanceGoblin.exe`.
3. Creates `MaintenanceGoblin.exe.sha256`.
4. Creates or updates the matching GitHub Release.
5. Attaches the executable and checksum.

The executable and installer are currently unsigned. Windows may therefore display an unknown-publisher or SmartScreen warning. File metadata does not constitute code signing.

## Versioning

Use Semantic Versioning. Keep the release version synchronized across:

- `pyproject.toml`
- `src/maintenance_goblin.py`
- `versionfile.txt` (numeric and string fields)
- `installer.nsi`
- the newest `CHANGELOG.md` entry

`tests/test_release_metadata.py` verifies this consistency.

## Safety and product boundaries

Do not add or claim:

- Registry cleaning
- RAM “boosting”
- Unsupported health or performance scores
- Aggressive process, service, or startup-item removal
- Destructive cleanup defaults
- Telemetry by default
- Advertising or bundled software

Prefer built-in Windows functionality, explicit descriptions, and read-only diagnostics. Long-running work must remain off the Tk main thread, and Tk widgets must only be updated on that thread.

## Architecture

The application is still centred on `src/maintenance_goblin.py`, supported by small modules for achievements, autostart, configuration, log delivery, project serialization, and update checking. Refactor incrementally when it improves current work; do not perform a speculative rewrite.

Resources must work both from source and from PyInstaller’s temporary bundle directory. Do not assume the executable directory is writable.

## Documentation and branding

Use “Maintenance Goblin” for the product name and `MaintenanceGoblin.exe` for the release binary. Keep wording concise, factual, and consistent with a safe Windows utility.

Current screenshots are:

- `docs/img/ui1.png` — Overview dashboard
- `docs/img/ui2.png` — Logs view

Do not refer to a History view, installer download, working automatic updates, code signing, task repair results, or other planned behaviour as complete.

## Future work

These are possible directions, not current features:

- Working GitHub release update checks
- Maintenance history and structured task results
- Maintenance profiles or scheduling
- System tray integration
- Configurable target drives
- Code-signed releases
- Automated installer builds
- Further separation of UI and maintenance logic

Implement future work only when explicitly requested and document it only after it is functional and tested.

## Working in this repository

Before changing behaviour:

1. Inspect the current implementation and tests.
2. Preserve conservative maintenance defaults and reliable elevation.
3. Keep background work thread-safe.
4. Test affected functionality.
5. Update versioned documentation and metadata when behaviour changes.

Prioritise safety, correctness, release reliability, clear feedback, and maintainability over adding surface area.
