from models.config import db
from marshmallow import Schema, fields

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    full_audio = db.Column(db.String(200), nullable=False)
    demo_segment = db.Column(db.String(200), nullable=False)
    cover = db.Column(db.String(200), nullable=False)
    dist_type = db.Column(db.Boolean, nullable=False)
    plays = db.Column(db.Integer, nullable=False, default=0)
    earnings = db.Column(db.Float, nullable=False, default=0)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Media {self.id} (title={self.title!r}\ttype={self.dist_type})>'.format(self=self)

class MediaSchema(Schema):
    mid = fields.Int(attribute='id')
    uid = fields.Int()
    title = fields.Str(required=True)
    full_audio = fields.Str(required=True)
    demo_segment = fields.Str(required=True)
    cover = fields.Str(required=True)
    dist_type = fields.Bool(required=True)
    plays = fields.Int()
    earnings = fields.Float()
