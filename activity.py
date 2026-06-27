from models import db, Activity, UnitSnapshot


def generate_activities(current_snapshot, previous_snapshot):

    if previous_snapshot is None:
        return

    previous_units = {
        (u.property_name, u.unit_name): u
        for u in previous_snapshot.units
    }

    current_units = {
        (u.property_name, u.unit_name): u
        for u in current_snapshot.units
    }

    for key, current_unit in current_units.items():

        previous_unit = previous_units.get(key)

        if previous_unit is None:
            continue

        current_rent = current_unit.rent or 0
        previous_rent = previous_unit.rent or 0

        current_status = current_unit.status or ""
        previous_status = previous_unit.status or ""

        #
        # Vacancy
        #
        if (
            previous_status != "Vacant-Unrented"
            and current_status == "Vacant-Unrented"
        ):
            activity = Activity(
                event_date=current_snapshot.snapshot_date,
                event_type="vacancy",
                property_name=current_unit.property_name,
                unit_name=current_unit.unit_name,
                description="Occupied → Vacant"
            )

            db.session.add(activity)

        #
        # Reoccupied
        #
        elif (
            previous_status == "Vacant-Unrented"
            and current_status != "Vacant-Unrented"
        ):
            activity = Activity(
                event_date=current_snapshot.snapshot_date,
                event_type="reoccupied",
                property_name=current_unit.property_name,
                unit_name=current_unit.unit_name,
                old_rent=previous_rent,
                new_rent=current_rent,
                description=f"Vacant → Occupied (${current_rent:,.0f})"
            )

            db.session.add(activity)

        #
        # Rent increase
        #
        elif (
            current_rent > 0
            and previous_rent > 0
            and current_rent != previous_rent
        ):

            percent_change = (
                (current_rent - previous_rent)
                / previous_rent
            ) * 100

            activity = Activity(
                event_date=current_snapshot.snapshot_date,
                event_type="rent_increase",
                property_name=current_unit.property_name,
                unit_name=current_unit.unit_name,
                old_rent=previous_rent,
                new_rent=current_rent,
                percent_change=percent_change,
                description=f"+{percent_change:.1f}% (${previous_rent:,.0f} → ${current_rent:,.0f})"
            )

            db.session.add(activity)

    db.session.commit()
