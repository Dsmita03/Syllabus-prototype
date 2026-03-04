from db.db import db

class Module(db.Model):
    id = db.Column(db.String, primary_key=True)
    syllabus_id = db.Column(db.String)
    name = db.Column(db.String)
    content = db.Column(db.String)