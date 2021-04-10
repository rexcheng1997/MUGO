from flask import Flask, request, jsonify
from models.config import *
from models.User import User, UserSchema
from models.Media import Media, MediaSchema
from models.Auction import Auction, AuctionSchema
from models.Bid import Bid, BidSchema
from models.Ownership import Ownership, OwnershipSchema

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_database_name}'

db.init_app(app)


@app.route('/init', methods=['PUT'])
def create_all_tables():
    with app.app_context():
        db.create_all()
    return '', 201


@app.route('/clear', methods=['DELETE'])
def drop_all_tables():
    with app.app_context():
        db.drop_all()
    return '', 200


@app.route('/all-users', methods=['GET'])
def retrieve_all_users():
    users = User.query.all()
    schema = UserSchema(exclude=('password', 'mnemonic'))
    return jsonify(*map(schema.dump, users)), 200


@app.route('/all-media', methods=['GET'])
def retrieve_all_media():
    media = Media.query.all()
    schema = MediaSchema()
    return jsonify(*map(schema.dump, media)), 200


@app.route('/create-user', methods=['POST'])
def create_user_endpoint():
    data = request.get_json()
    if data == None:
        return '', 400
    message = UserSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    # generate salt, hash password, encrypt mnemonic
    # by directly mutating the data object
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    schema = UserSchema(only=('uid', 'name', 'avatar', 'identity', 'subscription', 'created_at'))
    return schema.dump(user), 201


@app.route('/create-media', methods=['POST'])
def create_media_endpoint():
    data = request.get_json()
    if data == None:
        return '', 400
    message = MediaSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    media = Media(**data)
    db.session.add(media)
    db.session.commit()
    schema = MediaSchema()
    return schema.dump(media), 201


@app.route('/create-auction', methods=['POST'])
def create_auction_endpoint():
    data = request.get_json()
    if data == None:
        return '', 400
    message = AuctionSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    auction = Auction(**data)
    db.session.add(auction)
    db.session.commit()
    schema = AuctionSchema()
    return schema.dump(auction), 201


@app.route('/create-bid', methods=['POST'])
def create_bid_endpoint():
    data = request.get_json()
    if data == None:
        return '', 400
    message = BidSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    bid = Bid(**data)
    db.session.add(bid)
    db.session.commit()
    schema = BidSchema()
    return schema.dump(bid), 201
