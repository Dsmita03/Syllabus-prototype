from db.db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)  # Clerk user id
    email = db.Column(db.String, unique=True)

    syllabi = db.relationship("Syllabus", backref="user", lazy=True)