# Maintenance Goblin

A polished Windows desktop utility that wraps SFC, DISM, temporary file cleanup, Disk Cleanup, and defrag in a single window. Logs stream live with progress indicators and no disruptive pop-ups.

## Features
- One-click "Run All Tasks"
- Live in-app logs and progress
- Safe admin elevation before the GUI starts
- Optional read-only CHKDSK
- Exportable report of actions taken

## Installation (development)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/maintenance_goblin.py
```

## Build Windows EXE
```bash
pyinstaller --onefile --windowed --name "MaintenanceGoblin" ^
  --icon docs/img/goblin.ico src/maintenance_goblin.py
```

## Documentation
See the [documentation](docs/index.md) for screenshots and additional details.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License
Licensed under the [MIT License](LICENSE).
