from db.db import db
import uuid

class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))

    module_id = db.Column(
        db.String,
        db.ForeignKey("modules.id"),
        nullable=False
    )

    title = db.Column(db.String)
    url = db.Column(db.String)
    type = db.Column(db.String)

    extra_data = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, server_default=db.func.now())