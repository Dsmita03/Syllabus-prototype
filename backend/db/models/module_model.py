from db.db import db
import uuid

class Module(db.Model):
    __tablename__ = "modules"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))

    syllabus_id = db.Column(
        db.String,
        db.ForeignKey("syllabus.id"),
        nullable=False
    )

    name = db.Column(db.String)
    content = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    resources = db.relationship("Resource", backref="module", lazy=True)