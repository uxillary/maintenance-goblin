# Maintenance Goblin

Maintenance Goblin is a playful Windows utility that automates common
system maintenance chores such as SFC, DISM, CHKDSK, temporary file
cleanup, and drive optimization. This repository hosts the open-source
rewrite of the original script as it evolves into a distributable Python
application.

## Features
- Run several Windows maintenance commands with one click
- Individual task selection with a playful progress indicator
- Simple GUI powered by [`ttkbootstrap`](https://ttkbootstrap.readthedocs.io/)
- Live system information (CPU, RAM, OS) and toggleable log output
- Exportable reports and an optional ``--test`` mode for demos

## Installation
### Windows Executable
Download `MaintenanceGoblin.exe` from the
[releases](https://github.com/yourname/maintenance-goblin/releases) page and
run it. All logs and configuration files are stored under
`%APPDATA%/MaintenanceGoblin`.

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/yourname/maintenance-goblin.git
   cd maintenance-goblin
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Execute the application with Python:
```bash
python src/maintenance_goblin.py
```

### Debug & Silent Modes
Run with extra console output:
```bash
python src/maintenance_goblin.py --debug
```
Run all tasks without the GUI:
```bash
python src/maintenance_goblin.py --silent
```

### Command-Line Mode
Run specific tasks directly from the terminal:
```bash
python src/maintenance_goblin.py --cli --run-all
python src/maintenance_goblin.py --cli --sfc-only --export-log=output.txt
python src/maintenance_goblin.py --cli --cleanup-only
```
The `--export-log` option saves console output to the given file.

## Screenshot
Screenshot coming soon.

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for a complete history of changes.

## Version
Current release: **v0.1.0**

## Contributing
Contributions are welcome! Please open an issue or submit a pull request to
suggest improvements or report bugs.

## Author
Maintenance Goblin contributors

## License
This project is licensed under the [MIT License](LICENSE).
