import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Flask, render_template, request, redirect, url_for

from models import db, Snapshot, UnitSnapshot, Activity
from importer import import_rent_roll

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "rent_roll.db")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def dashboard():

    snapshots = (
        Snapshot.query
        .order_by(Snapshot.snapshot_date.desc())
        .all()
    )

    if not snapshots:
        return render_template(
            "dashboard.html",
            snapshot=None,
            chart_labels=[],
            gross_rents=[]
        )

    snapshot_date = request.args.get("snapshot_date")

    if snapshot_date:
        snapshot = Snapshot.query.filter_by(
            snapshot_date=datetime.strptime(
                snapshot_date,
                "%Y-%m-%d"
            ).date()
        ).first()
    else:
        snapshot = snapshots[0]

    # Subquery to find the latest rent increase date for each unit
    # on or before the current snapshot date
    latest_increase_sub = (
        db.session.query(
            Activity.property_name,
            Activity.unit_name,
            db.func.max(Activity.event_date).label("max_date")
        )
        .filter(
            Activity.event_type == "rent_increase",
            Activity.event_date <= snapshot.snapshot_date
        )
        .group_by(Activity.property_name, Activity.unit_name)
        .subquery()
    )

    # Join the subquery back to Activity to get the percent_change
    latest_activities = (
        db.session.query(
            Activity.property_name,
            Activity.unit_name,
            Activity.event_date,
            Activity.percent_change
        )
        .join(
            latest_increase_sub,
            db.and_(
                Activity.property_name == latest_increase_sub.c.property_name,
                Activity.unit_name == latest_increase_sub.c.unit_name,
                Activity.event_date == latest_increase_sub.c.max_date
            )
        )
        .filter(Activity.event_type == "rent_increase")
        .all()
    )

    # Create a lookup for activities by (property, unit)
    activity_lookup = {
        (a.property_name, a.unit_name): {
            "date": a.event_date,
            "percent_change": a.percent_change
        }
        for a in latest_activities
    }

    units_raw = (
        UnitSnapshot.query
        .filter_by(snapshot_id=snapshot.id)
        .order_by(
            UnitSnapshot.property_name,
            UnitSnapshot.unit_name
        )
        .all()
    )

    # Attach the latest activity to each unit object
    for unit in units_raw:
        activity = activity_lookup.get(
            (unit.property_name, unit.unit_name)
        )
        unit.last_increase = activity

        # Calculate next increase due (12 months after last increase)
        if activity:
            unit.next_increase_due = activity["date"] + relativedelta(years=1)
        else:
            unit.next_increase_due = None

    units = units_raw

    activities = (
        Activity.query
        .order_by(
            Activity.event_date.desc(),
            Activity.id.desc()
        )
        .limit(20)
        .all()
    )

    potential_gross = sum(
        unit.rent or 0
        for unit in units
    )

    chart_snapshots = (
        Snapshot.query
        .order_by(Snapshot.snapshot_date)
        .all()
    )

    chart_labels = []
    gross_rents = []

    for s in chart_snapshots:

        total = sum(
            unit.rent or 0
            for unit in s.units
        )

        chart_labels.append(
            s.snapshot_date.strftime("%b %Y")
        )

        gross_rents.append(total)

    return render_template(
        "dashboard.html",
        snapshot=snapshot,
        snapshots=snapshots,
        units=units,
        activities=activities,
        potential_gross=potential_gross,
        chart_labels=chart_labels,
        gross_rents=gross_rents
    )


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        file = request.files["file"]

        snapshot_date = datetime.strptime(
            request.form["snapshot_date"],
            "%Y-%m-%d"
        ).date()

        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        file.save(file_path)

        import_rent_roll(
            csv_path=file_path,
            snapshot_date=snapshot_date
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5050,
        debug=True
    )
