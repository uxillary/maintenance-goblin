# Changelog

## [0.2.0] - 2026-08-23
### Added
- Responsive maintenance dashboard with CPU, memory, and storage cards.
- Selectable per-task rows with queued, running, completed, and skipped states.
- Dedicated Overview, Logs, and Settings views.

### Changed
- Made Run Maintenance the primary action and moved theme, startup, and Gallery controls into Settings.
- Improved dark-theme readability with theme-aware, higher-contrast supporting text.
- Updated test mode so simulated maintenance does not require administrator elevation.

### Fixed
- Routed background maintenance updates through the Tk main thread to prevent unsafe widget access.
- Prevented CLI logging from crashing on Windows consoles that cannot encode Unicode status symbols.

## [0.1.2] - 2025-08-12
### Changed
- Refreshed documentation, license, and dependencies for the initial GitHub release.

## [0.1.1] - 2025-08-11
### Fixed
- Ensure elevated relaunch no longer passes the executable path as a parameter, allowing the GUI to open correctly.

## [0.1.0] - 2025-08-11
### Added
- First public release: GUI with Run All, SFC, DISM, Temp cleanup, Disk Cleanup, Defrag
- Live logs + progress, admin elevation, basic settings
