from flask import Flask, request, jsonify
from datetime import datetime
from models.config import *
from models.User import User, UserSchema
from models.Media import Media, MediaSchema
from models.Listener import Listener, ListenerSchema
from models.Auction import Auction, AuctionSchema
from models.Bid import Bid, BidSchema
from models.Ownership import Ownership, OwnershipSchema

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_database_name}'

db.init_app(app)

'''

INIT ROUTEs

'''
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


'''

USER ROUTERS

'''

@app.route('/all-users', methods=['GET'])
def retrieve_all_users():
    users = User.query.all()
    schema = UserSchema(exclude=('password', 'mnemonic'))
    return jsonify(*map(schema.dump, users)), 200


@app.route('/create-user', methods=['POST'])
def create_user_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    message = UserSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    user = User(**data)
    db.session.add(user)
    db.session.commit()

    schema = UserSchema(only=('uid', 'name', 'avatar', 'identity', 'subscription', 'createdAt'))
    return jsonify(schema.dump(user)), 201


@app.route('/get-user', methods=['POST'])
def login_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400

    # get user's checksum
    user = User.query.filter_by(email=data['email']).first()
    # evaluate if matches given checksum
    if user is None or data['password'] != user.password:
        return jsonify(message='User does not exist or password is not correct!'), 404

    schema = UserSchema(only=('uid', 'name', 'avatar', 'title', 'identity', 'mnemonic', 'subscription', 'createdAt'))
    user = schema.dump(user)

    if user['identity'] == 0: # artist
        releases = Media.query \
            .filter_by(uid=user['uid'], dist_type=False) \
            .order_by(Media.title) \
            .all()
        releases = MediaSchema(exclude=('uid', 'full_audio', 'demo_segment', 'dist_type')).dump(releases, many=True)
        for release in releases:
            release['artist'] = user['name']
        user['releases'] = releases

        auctions = Auction.query \
            .filter_by(uid=user['uid']) \
            .order_by(Auction.start.desc()) \
            .all()
        auctions = AuctionSchema(only=('aid', 'assetId', 'amount', 'start', 'end', 'sold', 'earnings', 'mid', 'media.title', 'media.cover')).dump(auctions, many=True)
        for auction in auctions:
            auction['cover'] = auction['media']['cover']
            auction['title'] = auction['media']['title']
            auction['artist'] = user['name']
            del auction['media']
        user['auctions'] = auctions

    else: # listener
        owns = Ownership.query.filter_by(uid=user['uid']).all()
        owns = OwnershipSchema(only=('aid', 'auction.assetId', 'auction.sold', 'auction.earnings', 'mid', 'media.uid', 'media.title', 'media.cover')).dump(owns, many=True)
        for own in owns:
            own['assetId'] = own['auction']['assetId']
            own['sold'] = own['auction']['sold']
            own['earnings'] = own['auction']['earnings']
            own['title'] = own['media']['title']
            own['cover'] = own['media']['cover']
            own['artist'] = User.query.get(own['media']['uid']).name
            del own['auction']
            del own['media']
        user['owns'] = owns

    return jsonify(user), 200


@app.route('/get-user/<int:uid>', methods=['GET'])
def get_user_endpoint(uid):

    # get user's checksum
    user = User.query.get(uid)
    # evaluate if matches given checksum
    if user is None:
        return jsonify(message=f'User {uid} does not exist!'), 404

    schema = UserSchema(only=('uid', 'name', 'avatar', 'title', 'identity', 'mnemonic', 'subscription', 'createdAt'))
    user = schema.dump(user)

    if user['identity'] == 0: # artist
        releases = Media.query \
            .filter_by(uid=user['uid'], dist_type=False) \
            .order_by(Media.title) \
            .all()
        releases = MediaSchema(exclude=('uid', 'full_audio', 'demo_segment', 'dist_type')).dump(releases, many=True)
        for release in releases:
            release['artist'] = user['name']
        user['releases'] = releases

        auctions = Auction.query \
            .filter_by(uid=user['uid']) \
            .order_by(Auction.start.desc()) \
            .all()
        auctions = AuctionSchema(only=('aid', 'assetId', 'amount', 'start', 'end', 'sold', 'earnings', 'mid', 'media.title', 'media.cover')).dump(auctions, many=True)
        for auction in auctions:
            auction['cover'] = auction['media']['cover']
            auction['title'] = auction['media']['title']
            auction['artist'] = user['name']
            del auction['media']
        user['auctions'] = auctions

    else: # listener
        owns = Ownership.query.filter_by(uid=user['uid']).all()
        owns = OwnershipSchema(only=('aid', 'auction.assetId', 'auction.sold', 'auction.earnings', 'mid', 'media.uid', 'media.title', 'media.cover')).dump(owns, many=True)
        for own in owns:
            own['assetId'] = own['auction']['assetId']
            own['sold'] = own['auction']['sold']
            own['earnings'] = own['auction']['earnings']
            own['title'] = own['media']['title']
            own['cover'] = own['media']['cover']
            own['artist'] = User.query.get(own['media']['uid']).name
            del own['auction']
            del own['media']
        user['owns'] = owns

    return jsonify(user), 200


@app.route('/get-mnemonic', methods=['GET'])
def get_mnemonic_endpoint():
    uid = None
    if request.args.get('uid'):
        uid = request.args.get('uid', type=int)
    elif request.args.get('mid'):
        uid = Media.query.get(request.args.get('mid', type=int)).uid
    if uid is None:
        return '', 400

    user = User.query.get(uid)
    if user is None:
        return jsonify(message=f'User {uid} does not exist!'), 404

    # decrypt the mnemonic
    return jsonify(mnemonic=user.mnemonic), 200


@app.route('/subscribe', methods=['POST'])
def subscribe_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'uid' not in data:
        return jsonify(message='Missing uid'), 400

    user = User.query.get(data['uid'])
    if user is None:
        return jsonify(message=f'User {data["uid"]} does not exist!'), 404

    user.subscription = datetime.now().astimezone()
    db.session.commit()
    return '', 200

'''

MEDIA ROUTES

'''

@app.route('/all-media', methods=['GET'])
def retrieve_all_media():
    media = Media.query.all()
    schema = MediaSchema()
    return jsonify(*map(schema.dump, media)), 200


@app.route('/releases', methods=['GET'])
def retrieve_all_releases():
    releases = Media.query \
        .filter_by(dist_type=False) \
        .order_by(Media.title) \
        .all()
    releases = MediaSchema(exclude=('full_audio', 'demo_segment', 'dist_type', 'listeners')).dump(releases, many=True)
    for release in releases:
        release['artist'] = User.query.get(release['uid']).name
    return jsonify(data=releases), 200


@app.route('/song/<int:mid>/<string:secret>', methods=['GET'])
def get_song_endpoint(mid, secret):
    song = Media.query.get(mid)
    if song is None:
        return '', 400

    song = MediaSchema().dump(song)
    if secret == '^mUg0_6o$':
        song['audio'] = song['full_audio']
    else:
        song['audio'] = song['demo_segment']
    del song['full_audio']
    del song['demo_segment']

    song['artist'] = User.query.get(song['uid']).name
    del song['uid']

    for listener in song['listeners']:
        user = User.query.get(listener['uid'])
        listener['name'] = user.name
        listener['avatar'] = user.avatar
        del listener['uid']

    return jsonify(song), 200


@app.route('/create-media', methods=['POST'])
def create_media_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    message = MediaSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    media = Media(**data)
    db.session.add(media)
    db.session.commit()
    schema = MediaSchema()
    return jsonify(schema.dump(media)), 201


@app.route('/add-listener-history', methods=['POST'])
def add_listener_history_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    message = ListenerSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    listener = Listener.query.filter_by(uid=data['uid'], mid=data['mid']).first()
    if listener is None:
        listener = Listener(**data)
        db.session.add(listener)
    else:
        listener.date = datetime.now().astimezone()

    media = Media.query.get(data['mid'])
    media.plays += 1

    db.session.commit()
    schema = ListenerSchema()
    return jsonify(schema.dump(listener)), 201


@app.route('/increment-song-tips', methods=['POST'])
def increment_song_tips_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'mid' not in data or 'amount' not in data:
        return jsonify(message='Missing data in the request'), 400

    song = Media.query.get(data['mid'])
    song.earnings += data['amount']
    db.session.commit()
    schema = MediaSchema(only=('mid', 'earnings'))
    return jsonify(schema.dump(song)), 200

'''

AUCTION ROUTES

'''

@app.route('/all-auctions', methods=['GET'])
def retrieve_all_auctions():
    auctions = Auction.query.all()
    schema = AuctionSchema()
    return jsonify(*map(schema.dump, auctions)), 200


@app.route('/all-bids', methods=['GET'])
def retrieve_all_bids():
    bids = Bid.query.all()
    schema = BidSchema()
    return jsonify(*map(schema.dump, bids)), 200


@app.route('/all-ownerships', methods=['GET'])
def retrieve_all_ownerships():
    ownerships = Ownership.query.all()
    schema = OwnershipSchema()
    return jsonify(*map(schema.dump, ownerships)), 200


@app.route('/auctions', methods=['GET'])
def get_all_auctions_endpoint():
    ts = datetime.utcnow()
    schema = AuctionSchema(exclude=('assetId', 'contractId', 'minBid', 'media', 'bids'))
    upcoming = Auction.query.filter(Auction.end > ts).order_by(Auction.start).all()
    upcoming = schema.dump(upcoming, many=True)
    finished = Auction.query.filter(Auction.end <= ts).order_by(Auction.start).all()
    finished = schema.dump(finished, many=True)

    for auction in upcoming:
        media = Media.query.get(auction['mid'])
        auction['title'] = media.title
        auction['cover'] = media.cover
        auction['artist'] = User.query.get(auction['uid']).name
        del auction['uid']
    for auction in finished:
        media = Media.query.get(auction['mid'])
        auction['title'] = media.title
        auction['cover'] = media.cover
        auction['artist'] = User.query.get(auction['uid']).name
        del auction['uid']

    return jsonify(upcoming=upcoming, finished=finished), 200


@app.route('/auction/<int:aid>/<int:uid>', methods=['GET'])
def get_auction_endpoint(aid, uid):
    auction = Auction.query.get(aid)
    if auction is None:
        return '', 404

    auction = AuctionSchema(only=('aid', 'uid', 'assetId', 'start', 'end', 'amount', 'minBid', 'sold', 'earnings', 'media.title', 'media.full_audio', 'media.demo_segment', 'media.cover')).dump(auction)

    auction['artist'] = User.query.get(auction['uid']).name
    auction['title'] = auction['media']['title']
    auction['cover'] = auction['media']['cover']
    if Ownership.query.filter_by(uid=uid, aid=aid).first() is None:
        auction['demo'] = auction['media']['demo_segment']
    else:
        auction['demo'] = auction['media']['full_audio']
    del auction['uid']
    del auction['media']

    participants = Bid.query.filter_by(aid=aid).order_by(Bid.bid.desc()).all()
    participants = BidSchema(only=('uid', 'bid')).dump(participants, many=True)
    for participant in participants:
        user = User.query.get(participant['uid'])
        participant['name'] = user.name
        participant['avatar'] = user.avatar
        del participant['uid']
    auction['participants'] = participants

    return jsonify(auction), 200


@app.route('/create-auction', methods=['POST'])
def create_auction_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400

    message = AuctionSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    auction = Auction(**data)
    db.session.add(auction)
    db.session.commit()
    schema = AuctionSchema()
    return jsonify(schema.dump(auction)), 201


@app.route('/update-auction', methods=['POST'])
def update_auction_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'aid' not in data:
        return jsonify(message='Missing aid in the request'), 400

    auction = Auction.query.get(data['aid'])
    if auction is None:
        return '', 404

    if 'assetId' in data:
        auction.assetId = data['assetId']
    if 'contractId' in data:
        auction.contractId = data['contractId']
    if 'sold' in data:
        auction.sold = data['sold']
    if 'earnings' in data:
        auction.earnings = data['earnings']
    db.session.commit()
    schema = AuctionSchema(exclude=('media',))
    return jsonify(schema.dump(auction)), 200


@app.route('/create-bid', methods=['POST'])
def create_bid_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    message = BidSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    bid = Bid(**data)
    db.session.add(bid)
    db.session.commit()
    schema = BidSchema()
    return jsonify(schema.dump(bid)), 201


@app.route('/delete-bid', methods=['DELETE'])
def delete_bid_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    message = BidSchema(only=('aid', 'uid')).validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    bid = Bid.query.filter_by(aid=data['aid'], uid=data['uid']).first()
    if bid is None:
        return '', 404

    db.session.delete(bid)
    db.session.commit()
    return jsonify(BidSchema().dump(bid)), 200


@app.route('/get-bids/<int:aid>', methods=['GET'])
def get_bids_endpoint(aid):
    auction = Auction.query.get(aid)
    if auction is None:
        return '', 404

    schema = AuctionSchema(only=('uid', 'mid', 'assetId', 'contractId', 'start', 'end', 'amount', 'minBid', 'bids.uid', 'bids.bid'))
    return jsonify(schema.dump(auction)), 200


@app.route('/create-ownership', methods=['POST'])
def create_ownership_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    message = OwnershipSchema().validate(data)
    if len(message) > 0:
        return jsonify(message), 400

    ownership = Ownership(**data)
    db.session.add(ownership)
    db.session.commit()
    schema = OwnershipSchema()
    return jsonify(schema.dump(ownership)), 201
