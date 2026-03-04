from db.db import db

class Syllabus(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String)
    title = db.Column(db.String)
    pdf_url = db.Column(db.String)
    status = db.Column(db.String)