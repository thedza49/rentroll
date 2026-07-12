# Rent Roll Portal

A Flask/SQLite dashboard for tracking a small rental property portfolio from
monthly rent roll CSV exports. Built to run on a Raspberry Pi.

## What it does

Each month, upload the CSV export from the property manager. The app:

- Stores the upload as a dated **snapshot** (one row per unit).
- Diffs it against the previous snapshot to build an **activity feed**
  (units going vacant, units being reoccupied, rent increases).
- Computes a **Next Increase** date per unit from activity history, since
  the property manager's export no longer reliably populates that column.
- Lets you page back through any past snapshot from a dropdown.

## Project structure

```
app.py              Flask routes: dashboard, snapshot selector, upload
models.py           SQLAlchemy models: Snapshot, UnitSnapshot, Activity
importer.py         Parses the uploaded CSV into a Snapshot + UnitSnapshots
activity.py         Diffs two snapshots into Activity rows (vacancy,
                     reoccupied, rent_increase)
templates/          dashboard.html, upload.html
static/style.css    Dashboard styling
docs/                Historical rent roll exports (CSV/XLSX), for reference
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `sample.env` to `.env` and adjust if needed.

## Running

```bash
source venv/bin/activate
python3 app.py
```

The app runs on `http://<host>:5050`. `uploads/` and `database/` are created
automatically on first run and are git-ignored.

## Uploading a rent roll

1. Go to **Upload Snapshot**.
2. Select the CSV export and the date it's "as of."
3. Submit. If a snapshot for that date already exists, it's replaced.

Expected CSV columns: `Unit, Status, Rent, Deposit, Lease From, Lease To,
Move-in, Move-out, Next Rent Increase Date`. Property names are inferred
from `-> ` marker rows in the `Unit` column, matching the property
manager's export format.

## Notes

- No authentication — intended for local/home-network use only.
- No systemd service configured; run manually via the command above.
- See `roadmap.md` for planned features.
