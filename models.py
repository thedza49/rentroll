from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Snapshot(db.Model):
    __tablename__ = "snapshots"

    id = db.Column(db.Integer, primary_key=True)

    snapshot_date = db.Column(
        db.Date,
        nullable=False,
        unique=True
    )

    imported_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    units = db.relationship(
        "UnitSnapshot",
        backref="snapshot",
        cascade="all, delete-orphan"
    )


class UnitSnapshot(db.Model):
    __tablename__ = "unit_snapshots"

    id = db.Column(db.Integer, primary_key=True)

    snapshot_id = db.Column(
        db.Integer,
        db.ForeignKey("snapshots.id"),
        nullable=False
    )

    property_name = db.Column(db.String(255))
    unit_name = db.Column(db.String(255))
    status = db.Column(db.String(100))
    rent = db.Column(db.Float, default=0)
    deposit = db.Column(db.Float, default=0)

    lease_from = db.Column(db.Date)
    lease_to = db.Column(db.Date)

    move_in_date = db.Column(db.Date)
    move_out_date = db.Column(db.Date)

    next_increase_date = db.Column(db.Date)


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)

    event_date = db.Column(
        db.Date,
        nullable=False
    )

    event_type = db.Column(
        db.String(50),
        nullable=False
    )

    property_name = db.Column(
        db.String(255)
    )

    unit_name = db.Column(
        db.String(255)
    )

    description = db.Column(
        db.Text
    )

    old_rent = db.Column(
        db.Float
    )

    new_rent = db.Column(
        db.Float
    )

    percent_change = db.Column(
        db.Float
    )
