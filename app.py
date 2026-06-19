import os
from datetime import datetime

from flask import (
Flask,
render_template,
request,
redirect,
url_for
)

from models import db, Snapshot, UnitSnapshot, Activity
from importer import import_rent_roll

BASE_DIR = os.path.abspath(os.path.dirname(**file**))

UPLOAD_FOLDER = os.path.join(
BASE_DIR,
"uploads"
)

DATABASE_PATH = os.path.join(
BASE_DIR,
"database",
"rent_roll.db"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(
os.path.join(BASE_DIR, "database"),
exist_ok=True
)

app = Flask(**name**)

app.config["SQLALCHEMY_DATABASE_URI"] = (
f"sqlite:///{DATABASE_PATH}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
db.create_all()

@app.route("/")
def dashboard():

```
snapshots = (
    Snapshot.query
    .order_by(Snapshot.snapshot_date.desc())
    .all()
)

if len(snapshots) == 0:
    return render_template(
        "dashboard.html",
        snapshot=None
    )

snapshot_date = request.args.get(
    "snapshot_date"
)

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
    .filter_by(
        snapshot_id=snapshot.id
    )
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
        u.rent or 0
        for u in s.units
    )

    chart_labels.append(
        s.snapshot_date.strftime("%b %Y")
    )

    gross_rents.append(
        round(total, 2)
    )

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
```

@app.route("/upload", methods=["GET", "POST"])
def upload():

```
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

return render_template(
    "upload.html"
)
```

if **name** == "**main**":
app.run(
host="0.0.0.0",
port=5000,
debug=True
)
