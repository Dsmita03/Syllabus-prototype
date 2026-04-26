from db.db import db
import uuid

class Syllabus(db.Model):
    __tablename__ = "syllabus"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = db.Column(
        db.String,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(db.String)
    pdf_url = db.Column(db.String)

    status = db.Column(db.String, default="PROCESSING")  
    # PROCESSING | COMPLETED | FAILED

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    modules = db.relationship("Module", backref="syllabus", lazy=True)
    outcomes = db.relationship("Outcome", backref="syllabus", lazy=True)