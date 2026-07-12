"""
One-time migration: rename existing "1", "2", "3", "4" unit names for
752 N 26th St. to "752 Unit 1", "752 Unit 2", etc., to match the
importer's new naming convention (see importer.py).

This updates every historical UnitSnapshot and Activity row so old and
newly-imported snapshots still line up correctly by (property_name,
unit_name) when building the activity feed.

Safe to run more than once — already-renamed rows are skipped.

Usage (from the project root, with the venv active):
    python3 migrate_26th_st_units.py
"""

from app import app
from models import db, UnitSnapshot, Activity

OLD_UNIT_NAMES = ["1", "2", "3", "4"]
PROPERTY_MATCH = "752 N 26th St"


def migrate():
    with app.app_context():

        unit_snapshots_updated = 0
        activities_updated = 0

        for old_name in OLD_UNIT_NAMES:

            new_name = f"752 Unit {old_name}"

            unit_snapshots = UnitSnapshot.query.filter(
                UnitSnapshot.property_name.contains(PROPERTY_MATCH),
                UnitSnapshot.unit_name == old_name
            ).all()

            for unit in unit_snapshots:
                unit.unit_name = new_name
                unit_snapshots_updated += 1

            activities = Activity.query.filter(
                Activity.property_name.contains(PROPERTY_MATCH),
                Activity.unit_name == old_name
            ).all()

            for activity in activities:
                activity.unit_name = new_name
                activities_updated += 1

        db.session.commit()

        print(f"Updated {unit_snapshots_updated} UnitSnapshot row(s).")
        print(f"Updated {activities_updated} Activity row(s).")


if __name__ == "__main__":
    migrate()
