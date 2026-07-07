"""
One-time migration script.

Why this exists:
Older imports were done before two bugs were fixed:
  1. Move-in/Move-out dates were being read from the wrong CSV column
     name, so they were never actually saved.
  2. "Vacant-Rented" units weren't being recognized as vacant (only
     "Vacant-Unrented" was).

Those bugs are fixed in importer.py / activity.py, but existing snapshots
in the database were built before the fix, so they need to be re-imported
from the original CSVs to pick up the correction. This script finds the
original CSV for each existing snapshot date and re-imports it, which
also rebuilds the Recent Activity feed with the corrected logic.

Run this ONCE after pulling the updated code. It's safe to re-run if
something goes wrong partway - it always rebuilds from scratch.

Usage (from the rentroll project folder on the Pi):
    python3 rebuild_history.py
"""

import os
import re
import glob
from datetime import date

from flask import Flask

from models import db, Snapshot, Activity
from importer import import_rent_roll

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "rent_roll.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOCS_FOLDER = os.path.join(BASE_DIR, "docs")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def extract_date_from_filename(filename):
    """
    Handles both naming styles seen in this repo:
      rent_roll_2025_09_30.csv
      rent_roll-20260531.csv
    """

    match = re.search(r"(\d{4})[-_](\d{2})[-_](\d{2})", filename)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    match = re.search(r"(\d{4})(\d{2})(\d{2})", filename)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    return None


with app.app_context():

    existing_dates = {s.snapshot_date for s in Snapshot.query.all()}

    if not existing_dates:
        print("No snapshots found in the database. Nothing to rebuild.")
        raise SystemExit(0)

    #
    # Find every candidate source CSV, in both the uploads folder (where
    # files land when uploaded through the web form) and docs (where the
    # historical exports are checked into the repo).
    #
    candidate_files = (
        glob.glob(os.path.join(UPLOAD_FOLDER, "*.csv"))
        + glob.glob(os.path.join(DOCS_FOLDER, "*.csv"))
    )

    files_by_date = {}

    for path in candidate_files:
        found_date = extract_date_from_filename(os.path.basename(path))
        if found_date:
            files_by_date[found_date] = path

    matched_dates = sorted(set(files_by_date.keys()) & existing_dates)
    missing_dates = sorted(existing_dates - set(files_by_date.keys()))

    print(f"Snapshots in database: {len(existing_dates)}")
    print(f"Matching source CSVs found: {len(matched_dates)}")

    if missing_dates:
        print(
            "\nWARNING: no source CSV found for these existing snapshot "
            "dates. They will be left exactly as they are:"
        )
        for d in missing_dates:
            print(f"  {d}")

    activity_count = Activity.query.count()

    print(
        f"\nThis will delete all {activity_count} existing Recent Activity "
        f"entries and rebuild them from {len(matched_dates)} snapshots, "
        f"picking up corrected move-in/move-out dates along the way."
    )

    confirm = input("Continue? [y/N] ")

    if confirm.strip().lower() != "y":
        print("Cancelled. No changes made.")
        raise SystemExit(0)

    #
    # Activity rows have no foreign key back to a snapshot, so re-running
    # the importer alone would just pile new rows on top of the old ones.
    # Wipe them first.
    #
    Activity.query.delete()
    db.session.commit()

    for d in matched_dates:
        print(f"Re-importing {d} from {os.path.basename(files_by_date[d])} ...")
        import_rent_roll(files_by_date[d], d)

    print("\nDone. Recent Activity has been rebuilt with the corrected logic.")
