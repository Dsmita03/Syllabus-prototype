from db.db import db
import uuid

class Outcome(db.Model):
    __tablename__ = "outcomes"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))

    syllabus_id = db.Column(
        db.String,
        db.ForeignKey("syllabus.id"),
        nullable=False
    )

    outcomes = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, server_default=db.func.now())