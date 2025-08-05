# Maintenance Goblin

Maintenance Goblin is a playful Windows utility that automates common
system maintenance chores such as SFC, DISM, temporary file cleanup, and
drive optimization. This repository hosts the open-source rewrite of the
original script as it evolves into a distributable Python application.

## Features
- Run several Windows maintenance commands with one click
- Simple GUI powered by [`ttkbootstrap`](https://ttkbootstrap.readthedocs.io/)
- Logs command output for later review

## Installation
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

## Version
Current release: **v0.1.0**

## Contributing
Contributions are welcome! Please open an issue or submit a pull request to
suggest improvements or report bugs.

## Author
Maintenance Goblin contributors

## License
This project is licensed under the [MIT License](LICENSE).
