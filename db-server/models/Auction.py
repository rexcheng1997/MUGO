from models.config import db
from marshmallow import Schema, fields
from .Media import MediaSchema
from .Bid import BidSchema

class Auction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assetId = db.Column(db.Integer)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    minBid = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Integer)
    earnings = db.Column(db.Float)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mid = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)

    media = db.relationship('Media', backref=db.backref('auction', lazy='select'), uselist=False, lazy='select')
    bids = db.relationship('Bid', backref=db.backref('auction', lazy='select'), lazy='select')

    def __repr__(self):
        return '<Auction {self.id} (asset_id={self.asset_id!r})>'.format(self=self)

class AuctionSchema(Schema):
    aid = fields.Int(attribute='id')
    uid = fields.Int(required=True)
    mid = fields.Int(required=True)
    assetId = fields.Int()
    start = fields.DateTime(required=True)
    end = fields.DateTime(required=True)
    amount = fields.Int(required=True)
    minBid = fields.Float(required=True)
    sold = fields.Int()
    earnings = fields.Float()
    media = fields.Nested(MediaSchema)
    bids = fields.List(fields.Nested(BidSchema))
