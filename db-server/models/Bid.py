from models.config import db
from marshmallow import Schema, fields

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bid = db.Column(db.Float, nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    aid = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)

    def __repr__(self):
        return '<Bid {self.id} (amount={self.amount!r}\tuser={self.uid}\tauction {self.aid})>'.format(self=self)

class BidSchema(Schema):
    bid = fields.Float(required=True)
    uid = fields.Int(required=True)
    aid = fields.Int(required=True)
