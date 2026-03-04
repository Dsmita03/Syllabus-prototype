from db.db import db

class Outcome(db.Model):
    id = db.Column(db.String, primary_key=True)
    syllabus_id = db.Column(db.String)
    outcomes = db.Column(db.JSON)