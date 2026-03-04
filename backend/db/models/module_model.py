from db.db import db

class Module(db.Model):
    __tablename__ = "modules"

    id = db.Column(db.String, primary_key=True)

    syllabus_id = db.Column(
        db.String,
        db.ForeignKey("syllabus.id"),
        nullable=False
    )

    name = db.Column(db.String)
    content = db.Column(db.Text)

    resources = db.relationship("Resource", backref="module", lazy=True)