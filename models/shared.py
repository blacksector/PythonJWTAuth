from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4

from flask_marshmallow import Marshmallow


db = SQLAlchemy()
ma = Marshmallow()

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


