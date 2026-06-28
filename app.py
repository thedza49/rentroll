import os
from datetime import datetime

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


@app.template_filter("short_property")
def short_property_filter(value):
    """
    Property names in the source export repeat themselves, e.g.
    "2366-2368 N 44th St. (Duplex) - 2366-2368 N 44th St. Milwaukee, WI 53210"
    Show only the part before the first " - " for a cleaner label.
    """
    if not value:
        return value

    return value.split(" - ")[0].strip()


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

    units = (
        UnitSnapshot.query
        .filter_by(snapshot_id=snapshot.id)
        .order_by(
            UnitSnapshot.property_name,
            UnitSnapshot.unit_name
        )
        .all()
    )

    activities = (
        Activity.query
        .order_by(
            Activity.event_date.desc(),
            Activity.id.desc()
        )
        .limit(20)
        .all()
    )

    return render_template(
        "dashboard.html",
        snapshot=snapshot,
        snapshots=snapshots,
        units=units,
        activities=activities
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
