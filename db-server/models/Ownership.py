from models.config import db
from marshmallow import Schema, fields
from .Media import MediaSchema
from .Auction import AuctionSchema

class Ownership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    aid = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)
    mid = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)

    auction = db.relationship('Auction', backref=db.backref('ownership', lazy='select'), uselist=False, lazy='joined')
    media = db.relationship('Media', backref=db.backref('ownership', lazy='select'), uselist=False, lazy='joined')

    def __repr__(self):
        return '<Ownership {self.id} (media={self.mid}\tuser={self.uid})>'.format(self=self)

class OwnershipSchema(Schema):
    uid = fields.Int(required=True)
    aid = fields.Int(required=True)
    mid = fields.Int(required=True)
    auction = fields.Nested(AuctionSchema, only=('aid', 'uid', 'mid', 'assetId'))
    media = fields.Nested(MediaSchema, exclude=('full_audio', 'demo_segment'))
