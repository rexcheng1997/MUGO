from models.config import db
from marshmallow import Schema, fields
from datetime import datetime
from .Media import MediaSchema
from .Auction import AuctionSchema
from .Ownership import OwnershipSchema

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # autoincrement=True by default
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    avatar = db.Column(db.String(200), nullable=False, default='images/default-avatar.png')
    password = db.Column(db.String(150), nullable=False)
    mnemonic = db.Column(db.String(500), nullable=False)
    identity = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100))
    subscription = db.Column(db.DateTime)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now().astimezone)

    media = db.relationship('Media', backref=db.backref('user', lazy='joined'), lazy='select')
    auctions = db.relationship('Auction', backref=db.backref('user', lazy='joined'), lazy='select')
    owns = db.relationship('Ownership', backref=db.backref('user', lazy='joined'), lazy='select')

    def __repr__(self):
        return '<User {self.id} (name={self.name!r}\temail={self.email!r})>'.format(self=self)

class UserSchema(Schema):
    uid = fields.Int(attribute='id')
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    avatar = fields.Str()
    password = fields.Str(required=True)
    mnemonic = fields.Str(required=True)
    identity = fields.Int(required=True)
    title = fields.Str()
    subscription = fields.DateTime()
    createdAt = fields.DateTime()
    media = fields.List(fields.Nested(MediaSchema, exclude=('full_audio', 'demo_segment')))
    auctions = fields.List(fields.Nested(AuctionSchema, exclude=('media', 'bids')))
    owns = fields.List(fields.Nested(OwnershipSchema, exclude=('media',)))
