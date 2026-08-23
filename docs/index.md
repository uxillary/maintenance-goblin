# Maintenance Goblin

Maintenance Goblin is a transparent Windows maintenance dashboard for SFC, DISM, read-only CHKDSK, temporary-file cleanup, Disk Cleanup, and Windows drive optimization.

## Dashboard

The Overview shows live CPU, memory, and system-storage context. Choose tasks from the maintenance plan, select **Run Maintenance**, and follow each task’s status and overall progress. Detailed command output remains available in the separate Logs view.

Secondary preferences—including light/dark theme, launch at startup, and the achievement Gallery—are grouped under Settings.

## Safe local test

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\src\maintenance_goblin.py --test
```

Test mode simulates maintenance without elevation or Windows system changes. Omit `--test` only when you intend to run the real maintenance commands.

## Screenshot

The screenshots below show an earlier interface and will be refreshed for version 0.2.0.

![Earlier Maintenance Goblin interface](img/ui-1.png)
