from db.db import db

class Resource(db.Model):
    id = db.Column(db.String, primary_key=True)
    module_id = db.Column(db.String)   # which module this belongs to
    title = db.Column(db.String)
    url = db.Column(db.String)
    type = db.Column(db.String)        # video / article / pdf etc.
    extra_data = db.Column(db.JSON) 