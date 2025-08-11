# Maintenance Goblin

A polished Windows desktop utility that runs SFC, DISM, temp cleanup, Disk Cleanup, and defrag — with live logs, progress, and no popups.

## Features
- One-click “Run All Tasks”
- Live in-app logs and progress
- Safe admin elevation before GUI
- Optional CHKDSK (read-only)
- Exportable report

## Install (dev)
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

## Screenshots

## Contributing
See CONTRIBUTING.md.

## License
MIT
