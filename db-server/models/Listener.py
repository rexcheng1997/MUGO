from models.config import db
from marshmallow import Schema, fields
from datetime import datetime

class Listener(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now().astimezone)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mid = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)

    def __repr__(self):
        return '<Listener {self.id} (user={self.uid!r}\tmedia={self.mid!r})>'.format(self=self)

class ListenerSchema(Schema):
    uid = fields.Int(required=True)
    mid = fields.Int(required=True)
    date = fields.DateTime()
