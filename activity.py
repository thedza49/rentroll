from models import db, Activity, UnitSnapshot, Snapshot

#
# The export uses two different labels for a vacant unit depending on
# whether it's already been leased to a future tenant. Both mean the
# unit is NOT currently occupied.
#
VACANT_STATUSES = {"Vacant-Unrented", "Vacant-Rented"}


def find_last_occupied_unit(property_name, unit_name, before_date):
    """
    Walk backwards through snapshot history (older than before_date) to find
    the most recent snapshot where this unit actually had rent coming in.
    This is needed because the snapshot right before a unit is reoccupied
    usually shows $0 rent (it was vacant), so we can't just look at the
    single previous snapshot for the "last rent" comparison.
    """

    return (
        db.session.query(UnitSnapshot)
        .join(Snapshot, UnitSnapshot.snapshot_id == Snapshot.id)
        .filter(
            UnitSnapshot.property_name == property_name,
            UnitSnapshot.unit_name == unit_name,
            Snapshot.snapshot_date < before_date,
            UnitSnapshot.rent > 0
        )
        .order_by(Snapshot.snapshot_date.desc())
        .first()
    )


def format_vacancy_duration(days):
    """
    Turn a day count into a friendly string, e.g. "18 days" or "3 months".
    """

    if days is None or days < 0:
        return None

    if days < 60:
        return f"{days} day{'s' if days != 1 else ''}"

    months = round(days / 30.44)

    return f"~{months} months ({days} days)"


def generate_activities(current_snapshot, previous_snapshot):

    #
    # Clear out any activities already recorded for this snapshot's date
    # before regenerating them. Without this, re-importing a date that's
    # already been processed (e.g. re-running seed_data.py, or re-uploading
    # a snapshot) creates duplicate activity rows instead of replacing them.
    #
    Activity.query.filter_by(
        event_date=current_snapshot.snapshot_date
    ).delete()

    db.session.commit()

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
            previous_status not in VACANT_STATUSES
            and current_status in VACANT_STATUSES
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
            previous_status in VACANT_STATUSES
            and current_status not in VACANT_STATUSES
        ):
            last_occupied_unit = find_last_occupied_unit(
                property_name=current_unit.property_name,
                unit_name=current_unit.unit_name,
                before_date=current_snapshot.snapshot_date
            )

            #
            # Figure out the rent to compare against (the last rent we
            # actually collected on this unit, not the $0 from the
            # vacant snapshot) and how long it sat vacant.
            #
            last_rent = None
            vacancy_days = None

            if last_occupied_unit:

                last_rent = last_occupied_unit.rent

                vacancy_start = (
                    last_occupied_unit.move_out_date
                    or last_occupied_unit.snapshot.snapshot_date
                )

                vacancy_end = (
                    current_unit.move_in_date
                    or current_snapshot.snapshot_date
                )

                vacancy_days = (vacancy_end - vacancy_start).days

            if last_rent:

                percent_change = (
                    (current_rent - last_rent)
                    / last_rent
                ) * 100

                sign = "+" if percent_change >= 0 else ""

                description = (
                    f"{sign}{percent_change:.1f}% "
                    f"(${last_rent:,.0f} → ${current_rent:,.0f})"
                )

            else:
                #
                # No prior rent on record for this unit (e.g. first
                # snapshot ever imported for it) — fall back gracefully.
                #
                percent_change = None
                description = f"Vacant → Occupied (${current_rent:,.0f})"

            duration_text = format_vacancy_duration(vacancy_days)

            if duration_text:
                description += f" • Vacant {duration_text}"

            activity = Activity(
                event_date=current_snapshot.snapshot_date,
                event_type="reoccupied",
                property_name=current_unit.property_name,
                unit_name=current_unit.unit_name,
                old_rent=last_rent if last_rent else previous_rent,
                new_rent=current_rent,
                percent_change=percent_change,
                description=description
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
