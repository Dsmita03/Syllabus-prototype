from db.db import db
import uuid

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    syllabi = db.relationship("Syllabus", backref="user", lazy=True)