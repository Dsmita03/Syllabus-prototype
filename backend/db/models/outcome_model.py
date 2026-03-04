from db.db import db

class Outcome(db.Model):
    __tablename__ = "outcomes"

    id = db.Column(db.String, primary_key=True)

    syllabus_id = db.Column(
        db.String,
        db.ForeignKey("syllabus.id"),
        nullable=False
    )

    outcomes = db.Column(db.JSON)