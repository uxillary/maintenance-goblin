# Maintenance Goblin — Project Context

## Overview

**Maintenance Goblin** is a lightweight Windows desktop maintenance and diagnostic utility written in Python.

It provides a friendly GUI around legitimate Windows maintenance tools such as SFC, DISM, CHKDSK, temporary-file cleanup and drive optimisation.

The project started as a simple Tkinter script and is evolving into a polished, safe and professional open-source Windows utility.

**Current release target:** `v0.2.0`

---

## Product Philosophy

Maintenance Goblin should make Windows maintenance:

- Easier to understand
- Safer to perform
- More transparent
- Visually approachable
- Less intimidating for non-technical users

The application has a playful goblin identity, but underlying system operations should always be presented professionally and accurately.

### Avoid "PC Optimizer" nonsense

Do **not** turn Maintenance Goblin into a questionable one-click optimiser.

Avoid:

- Registry cleaners
- Fake performance improvements
- RAM "boosters"
- Aggressive process killing
- Unnecessary service disabling
- Misleading health scores
- Destructive cleanup defaults
- Telemetry by default
- Bundled software
- Advertising

Prefer built-in Windows functionality and clearly explain what each operation actually does.

---

## Technology

Current stack:

- Python
- Tkinter
- `ttkbootstrap`
- `psutil`
- PyInstaller
- Git / GitHub
- GitHub Releases
- GitHub Pages

Primary platform:

**Windows 10 / Windows 11**

Main application entry point:

`src/maintenance_goblin.py`

Current packaged application:

`MaintenanceGoblin.exe`

---

## Current Functionality

### System File Checker

Uses:

`SFC /scannow`

Detects and repairs protected Windows system-file corruption.

### DISM

Uses Windows DISM health/repair functionality including:

`DISM /Online /Cleanup-Image /RestoreHealth`

Used to inspect and repair the Windows component store.

### Temporary File Cleanup

Removes appropriate temporary files while safely ignoring files currently locked or in use.

Where practical, report:

- Files removed
- Files skipped
- Approximate storage recovered

### Windows Disk Cleanup

Provides access to Windows' built-in cleanup functionality rather than implementing an unsafe custom cleaner.

### Drive Optimisation

Uses Windows drive optimisation functionality.

The application must distinguish conceptually between:

- HDD defragmentation
- SSD optimisation / TRIM

Never blindly treat SSDs as traditional HDDs requiring defragmentation.

### CHKDSK

CHKDSK should normally operate as a **read-only diagnostic**.

Repair options such as `/f`, `/r`, and `/x` must not run silently as routine maintenance.

If repair functionality is exposed later, clearly explain that it may require a reboot or filesystem dismount.

---

## User Experience

The preferred workflow is:

    Select maintenance tasks
            ↓
    Run Maintenance
            ↓
    Tasks execute sequentially
            ↓
    Live progress and status
            ↓
    Results summarised
            ↓
    Detailed logs available if wanted

Users should never press a button and wonder whether the application has frozen.

Long-running maintenance operations must not block the GUI.

---

## Main UI Direction

Maintenance Goblin should feel like a modern Windows system utility rather than a collection of default Tkinter controls.

The main screen should evolve toward a **maintenance dashboard**.

Example:

    Maintenance Goblin
    System status / readiness

    CPU        RAM        Storage
    12%        42%        135 GB free

    Maintenance

    ☑ System File Check          Ready
    ☑ Windows Image Repair       Ready
    ☑ Check Disk                 Ready
    ☑ Temporary Files            Ready
    ☑ Drive Optimisation         Ready

    Overall Progress

            Run Maintenance

    Overview | Logs | History

---

## System Statistics

Useful system information may include:

- CPU usage
- CPU model
- RAM usage
- Installed RAM
- Windows version
- System drive
- Disk capacity
- Free disk space
- Drive type where reliably detectable
- Application version
- Administrator/elevation state

System statistics should provide useful context.

For example:

    RAM
    22.8 / 24 GB
    95% used

High utilisation can be highlighted visually.

Do not imply that normal RAM usage automatically needs "cleaning".

---

## Task Feedback

Every maintenance task should have a clear state.

Suggested states:

- Ready
- Queued
- Running
- Completed
- Warning
- Failed
- Skipped

Example:

    ✓ System File Check       Healthy             4m 12s
    ✓ Windows Image Repair    Healthy             2m 08s
    ✓ Check Disk              No errors           1m 03s
    ✓ Temporary Files         487 MB recovered       8s
    ✓ Drive Optimisation      TRIM completed         6s

---

## Completion Summary

After maintenance finishes, provide a concise useful summary.

Example:

    Maintenance complete

    5/5 tasks completed
    487 MB recovered
    7m 37s total

Detailed raw command output belongs in the Logs view rather than dominating the main interface.

---

## Progress

Provide:

- Current task
- Per-task state
- Overall progress
- Task duration where useful

The progress indicator should reflect actual workflow progress where possible.

Avoid animations that imply measurable progress when none is available.

An indeterminate progress indicator is acceptable for commands where Windows does not expose reliable progress.

---

## Logs

Logs should primarily be available inside the application.

Avoid modal popups simply saying that a log was written.

Preferred behaviour:

    Task running
        ↓
    Status updates
        ↓
    Result shown
        ↓
    Detailed output available under Logs

Reports may also be exported manually.

---

## Reports

Exported reports may contain:

- Timestamp
- Maintenance Goblin version
- Windows version
- Tasks executed
- Result of each task
- Duration
- Warnings
- Errors
- Disk-space changes

Avoid unnecessarily exposing sensitive machine information.

---

## UI / Visual Identity

The application is called **Maintenance Goblin**.

The identity combines:

- Modern Windows utility
- Friendly system maintenance
- Slight goblin mischief
- Professional presentation

A custom goblin logo/icon exists and should be used consistently.

Preferred visual characteristics:

- Dark/light themes
- Modern dashboard layout
- Cards/panels
- Clear hierarchy
- Generous spacing
- Segoe UI or suitable Windows-native typography
- Clear primary action
- Semantic status colours
- Responsive/resizable window
- Minimal visual clutter

Avoid excessive default Tkinter styling.

---

## Primary vs Secondary Actions

The main action should be visually obvious:

**Run Maintenance**

or, where appropriate:

**Summon Goblin**

Secondary actions should not compete visually with maintenance controls.

Examples:

- Theme
- Run at startup
- Gallery
- Update settings
- Advanced options

These should generally live inside a **Settings** area rather than permanently occupying the main toolbar.

---

## Navigation

If Logs already exists as a dedicated tab/view, avoid redundant controls such as `Toggle Logs`.

Prefer clear navigation such as:

`Overview | Logs | History`

---

## Goblin Personality

Small amounts of humour are encouraged.

Examples:

- Summon Goblin
- Goblin working
- Goblin resting
- Small maintenance-related messages
- Optional achievements/easter eggs

However:

**Useful diagnostic information always takes priority over jokes.**

Errors must explain what actually went wrong.

---

## Administrator Privileges

Several maintenance commands require administrator privileges.

Elevation must happen before the final Tk/ttkbootstrap GUI is created.

A previous issue produced:

    _tkinter.TclError:
    can't invoke "tk" command:
    application has been destroyed

The application lifecycle should remain approximately:

    Start
      ↓
    Check elevation
      ↓
    Relaunch elevated if necessary
      ↓
    Create GUI
      ↓
    Run Tk mainloop

Avoid:

- Multiple Tk root instances
- Creating ttkbootstrap widgets before the final root exists
- Destroying/recreating the root unnecessarily

---

## Threading

Long-running Windows commands must execute outside Tkinter's main UI thread.

The GUI must remain responsive during:

- SFC
- DISM
- CHKDSK
- Drive optimisation
- Cleanup

Tkinter widgets should only be manipulated safely from the UI thread.

Maintenance logic should increasingly return structured results rather than directly modifying widgets.

---

## Architecture Direction

The application originated as a large single Python file.

Do not continue indefinitely expanding `maintenance_goblin.py`.

Refactor **incrementally**, preserving working functionality.

Long-term structure may resemble:

    src/
    └── maintenance_goblin/
        ├── __init__.py
        ├── __main__.py
        ├── app.py
        ├── ui/
        │   ├── dashboard.py
        │   ├── logs.py
        │   └── settings.py
        ├── tasks/
        │   ├── sfc.py
        │   ├── dism.py
        │   ├── chkdsk.py
        │   ├── cleanup.py
        │   └── optimize.py
        ├── services/
        ├── reporting/
        ├── config/
        └── utils/

Do not perform a giant rewrite simply to achieve this structure.

Move components only when doing so improves maintainability or enables current work.

---

## Structured Task Results

Maintenance operations should eventually return structured results.

Conceptually:

    TaskResult
    ├── task
    ├── status
    ├── summary
    ├── raw_output
    ├── duration
    ├── warnings
    └── error

This allows the same maintenance logic to support:

- GUI
- CLI
- Reports
- History
- Tests
- Scheduled maintenance

without duplicating functionality.

---

## Application Data

Do not assume the executable directory is writable.

User-specific data should eventually use an appropriate Windows location such as:

`%LOCALAPPDATA%\MaintenanceGoblin\`

Possible stored data:

    settings.json
    logs/
    reports/
    history.json
    achievements.json

---

## Packaging

Maintenance Goblin is packaged using PyInstaller.

Desired output:

`MaintenanceGoblin.exe`

The build currently uses:

- One-file executable
- Windowed mode
- Custom `goblin.ico`
- Windows version metadata

Resources must resolve correctly both during Python development and inside the packaged PyInstaller executable.

Do not rely on the current working directory.

---

## Windows Metadata

The executable should contain appropriate Windows metadata including:

- Maintenance Goblin
- Application version
- Description
- Author/publisher information
- Copyright
- Project website

A PyInstaller-compatible version information file is used during builds.

---

## GitHub

Maintenance Goblin is intended to be a professional public GitHub project.

Important repository content includes:

    src/
    docs/
    .github/
    README.md
    CHANGELOG.md
    CONTRIBUTING.md
    CODE_OF_CONDUCT.md
    LICENSE
    requirements.txt
    pyproject.toml
    build.bat

Build output such as `build/` and `dist/` should normally remain ignored by Git.

---

## Releases

Use Semantic Versioning.

Current public release target:

`v0.2.0`

Examples:

- `0.1.1` — bug fixes
- `0.2.0` — backwards-compatible feature release
- `1.0.0` — stable mature release

Release assets should eventually include:

    MaintenanceGoblin.exe
    MaintenanceGoblin.exe.sha256

GitHub automatically provides source archives.

---

## GitHub Actions

The project should eventually have a reliable Windows release workflow.

Preferred release process:

    Update version
        ↓
    Update CHANGELOG
        ↓
    Commit
        ↓
    Tag vX.Y.Z
        ↓
    Push tag
        ↓
    GitHub Actions builds Windows executable
        ↓
    Executable attached to GitHub Release

Never publish a release automatically unless the workflow is intentionally configured and tested for that behaviour.

---

## GitHub Pages

A small GitHub Pages site should act as the project's public landing page/documentation.

It should eventually contain:

- Branding
- Description
- Screenshots
- Features
- Latest download
- Documentation
- Safety/transparency information
- GitHub repository link
- Report issue link

Keep the website visually consistent with the application.

---

## Security & Trust

Trust is especially important because Maintenance Goblin:

- Requests administrator privileges
- Executes Windows system commands
- Deletes temporary files
- Is distributed as an executable
- May trigger SmartScreen warnings while unsigned

Prefer:

- Open-source implementation
- Documented commands
- Conservative defaults
- Clear descriptions
- Explicit confirmation for destructive operations
- No telemetry by default
- No hidden background behaviour
- No registry cleaners
- No bundled software
- No advertisements
- Minimal network access

Any update checking or network functionality should be clearly documented.

---

## Potential Future Features

These are **ideas, not current requirements**.

Do not implement them simply because they appear here.

Possible future functionality:

- Maintenance history
- Maintenance profiles
- System tray integration
- Windows Task Scheduler integration
- CLI mode
- GitHub release update checking
- Goblin achievements
- Additional diagnostics
- Better system-health summaries

Implement future features only when they provide meaningful value.

---

## Development Priorities

When deciding what to work on, prioritise:

1. Safety
2. Bugs / regressions
3. Reliability
4. Correct Windows behaviour
5. Release blockers
6. Useful feedback
7. Maintainable architecture
8. UI/UX
9. Packaging
10. Documentation
11. New functionality
12. Goblin extras

Do not add features merely to make the project appear larger.

---

## Working With This Repository

Before making significant changes:

1. Read this file.
2. Inspect the existing implementation.
3. Check whether functionality already exists.
4. Preserve working behaviour.
5. Avoid duplicate systems.
6. Avoid unnecessary dependencies.
7. Prefer small coherent changes.
8. Test affected functionality.
9. Update documentation when behaviour changes.

Do not rewrite working components without a clear technical reason.

---

## Current Goal

The immediate goal is to turn Maintenance Goblin into a **credible, polished and safe public Windows utility**.

Current focus should be:

- Professional dashboard UI
- Reliable maintenance execution
- Clear per-task feedback
- Useful completion summaries
- Thread-safe GUI behaviour
- Reliable administrator elevation
- Clean application architecture
- Reliable PyInstaller builds
- Professional GitHub repository
- Repeatable release process

When choosing the next task, select the **single highest-value improvement** toward these goals rather than attempting several unrelated features simultaneously.
