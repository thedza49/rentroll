# Rent Roll Portal

A Flask/SQLite dashboard for tracking a small rental property portfolio from
monthly rent roll CSV exports. Built to run on a Raspberry Pi.

## What it does

Each month, upload the CSV export from the property manager. The app:

- Stores the upload as a dated **snapshot** (one row per unit).
- Diffs it against the previous snapshot to build an **activity feed**
  (units going vacant, units being reoccupied, rent increases) — shows
  the 12 most recent events.
- Computes a **Next Increase** date per unit from activity history, since
  the property manager's export no longer reliably populates that column.
- Shows a **total rent** row at the bottom of the Unit Inventory table.
- Plots **Financial Trends**: total rent (bars) and occupancy % (line)
  across every snapshot in history.
- Lets you page back through any past snapshot from a dropdown.

## Project structure

```
app.py                     Flask routes: dashboard, snapshot selector, upload
models.py                  SQLAlchemy models: Snapshot, UnitSnapshot, Activity
importer.py                Parses an uploaded CSV into a Snapshot + UnitSnapshots
activity.py                Diffs two snapshots into Activity rows (vacancy,
                            reoccupied, rent_increase)
seed_data.py                Bulk-imports every CSV in docs/ in one run, instead
                            of uploading each snapshot by hand
migrate_26th_st_units.py    One-time migration: renames legacy "1"-"4" unit
                            names at 752 N 26th St. to "752 Unit 1", etc.
                            Already run — kept for reference/re-running if
                            the database is ever rebuilt from old data.
templates/                 dashboard.html, upload.html
static/style.css           Dashboard styling
docs/                       Historical rent roll exports (CSV/XLSX), for reference
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

## Bulk-loading historical data

To load every CSV in `docs/` at once (e.g. after rebuilding the database
from scratch) instead of uploading each snapshot by hand:

```bash
source venv/bin/activate
python3 seed_data.py
```

It sorts files by filename and imports them in order, so the activity feed
builds up correctly across the full history. Handles both filename formats
used over time (`rent_roll_YYYY_MM_DD.csv` and `rent_roll-YYYYMMDD.csv`).

## Uploading a rent roll

1. Go to **Upload Snapshot**.
2. Select the CSV export and the date it's "as of."
3. Submit. If a snapshot for that date already exists, it's replaced.

Expected CSV columns: `Unit, Status, Rent, Deposit, Lease From, Lease To,
Move-in, Move-out, Next Rent Increase Date`. Property names are inferred
from `-> ` marker rows in the `Unit` column, matching the property
manager's export format. Bare-numeric unit names (e.g. a 4-unit building
labeled just "1", "2", "3", "4") are automatically prefixed with the
building's street number, e.g. "752 Unit 1", to match the naming used for
other properties.

## Notes

- No authentication — intended for local/home-network use only.
- No systemd service configured; run manually via the command above.
- See `roadmap.md` for planned features.
