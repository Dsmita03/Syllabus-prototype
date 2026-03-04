from db.db import db

class Syllabus(db.Model):
    __tablename__ = "syllabus"

    id = db.Column(db.String, primary_key=True)

    user_id = db.Column(
        db.String,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(db.String)
    pdf_url = db.Column(db.String)
    status = db.Column(db.String)

    modules = db.relationship("Module", backref="syllabus", lazy=True)
    outcomes = db.relationship("Outcome", backref="syllabus", lazy=True)