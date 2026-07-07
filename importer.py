import pandas as pd

from models import db, Snapshot, UnitSnapshot
from activity import generate_activities

def parse_date(value):
    if pd.isna(value):
        return None

    try:
        return pd.to_datetime(value).date()
    except:
        return None


def parse_money(value):
    if pd.isna(value):
        return 0

    try:
        return float(str(value).replace("$", "").replace(",", ""))
    except:
        return 0


def import_rent_roll(csv_path, snapshot_date):

    #
    # Remove existing snapshot if it already exists
    #
    existing_snapshot = Snapshot.query.filter_by(
        snapshot_date=snapshot_date
    ).first()

    if existing_snapshot:
        db.session.delete(existing_snapshot)
        db.session.commit()

    #
    # Find previous snapshot before creating current
    #
    previous_snapshot = (
        Snapshot.query
        .filter(Snapshot.snapshot_date < snapshot_date)
        .order_by(Snapshot.snapshot_date.desc())
        .first()
    )

    #
    # Create new snapshot
    #
    snapshot = Snapshot(
        snapshot_date=snapshot_date
    )

    db.session.add(snapshot)
    db.session.commit()

    #
    # Read CSV
    #
    df = pd.read_csv(csv_path)

    #
    # Loop through rows
    #
    current_property = ""

    for _, row in df.iterrows():

        unit_name = str(row.get("Unit", "")).strip()

        if not unit_name or unit_name == "nan":
            continue

        if unit_name.startswith("->"):
            current_property = unit_name.replace("->", "").strip()
            continue

        if any(word in unit_name.lower() for word in ["total", "units"]):
            continue

        unit = UnitSnapshot(
            snapshot_id=snapshot.id,

            property_name=current_property,
            unit_name=unit_name,

            status=row.get("Status", ""),

            rent=parse_money(
                row.get("Rent", 0)
            ),

            deposit=parse_money(
                row.get("Deposit", 0)
            ),

            lease_from=parse_date(
                row.get("Lease From")
            ),

            lease_to=parse_date(
                row.get("Lease To")
            ),

            move_in_date=parse_date(
                row.get("Move-in")
            ),

            move_out_date=parse_date(
                row.get("Move-out")
            ),

            next_increase_date=parse_date(
                row.get("Next Rent Increase Date")
            )
        )

        db.session.add(unit)

    db.session.commit()

    #
    # Refresh snapshot so units relationship exists
    #
    db.session.refresh(snapshot)

    #
    # Build activity history
    #
    generate_activities(
        current_snapshot=snapshot,
        previous_snapshot=previous_snapshot
    )

    return snapshot
