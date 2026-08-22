# Maintenance Goblin

A friendly Windows maintenance utility.  
**Download:** See the GitHub Releases page.

## Features
- One-click Run All (SFC, DISM, cleanup, defrag)
- Live logs and progress indicators
- Safe admin elevation before the GUI starts
- Optional read-only CHKDSK
- Exportable report of actions taken

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/maintenance_goblin.py
```

## Screenshot
![UI](img/ui-1.png)
