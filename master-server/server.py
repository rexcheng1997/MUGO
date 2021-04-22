from .config import *
import os, re, requests, ffmpeg
from datetime import datetime
from flask import Flask, request, session, jsonify
from werkzeug.utils import secure_filename
import hashlib

app = Flask(__name__, static_url_path='/', static_folder=FLASK_STATIC_FOLDER, root_path=os.path.dirname(os.path.abspath(__file__)))
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['UPLOAD_FOLER'] = FLASK_UPLOAD_FOLDER

def get_hash(password):
    salted = password + password[0] 
    return hashlib.sha256(bytes(salted, 'utf-8')).hexdigest()

@app.route('/', methods=['GET'])
def on_start():
    requests.put(f'http://{DB_SERVER}/init')
    return app.send_static_file('index.html'), 200


@app.route('/signup', methods=['POST'])
def signup_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400

    r = requests.put(f'http://{BLOCKCHAIN_SERVER}/create-wallet')
    data['password'] = get_hash(data['password'])
    data['mnemonic'] = r.json()['mnemonic']

    r = requests.post(f'http://{DB_SERVER}/create-user', json=data)
    if r.status_code == 400:
        return jsonify(r.json()) if len(r.text) > 0 else '', 400
    
    return jsonify(status=True), 200


@app.route('/login', methods=['POST'])
def login_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400

    data['password'] = get_hash(data['password'])
    r = requests.post(f'http://{DB_SERVER}/get-user', json=data)
    if r.status_code == 400:
        return '', 400
    elif r.status_code == 404:
        return jsonify(r.json()) if len(r.text) > 0 else '', 404

    user = r.json()
    session['uid'] = user['uid']
    session['vip'] = user['subscription'] != None

    r = requests.post(f'http://{BLOCKCHAIN_SERVER}/check-wallet-balance', json={
        'passphrase': user['mnemonic']
    })
    user['balance'] = r.json()['balance']
    del user['mnemonic']

    return jsonify(user), 200


@app.route('/logout', methods=['POST'])
def logout_endpoint():
    if 'uid' in session:
        del session['uid']
    if 'vip' in session:
        del session['vip']
    return '', 200


@app.route('/user', methods=['GET'])
def get_user_endpoint():
    if 'uid' not in session:
        return '', 200

    r = requests.get(f'http://{DB_SERVER}/get-user/{session["uid"]}')
    if r.status_code == 404:
        return jsonify(r.json()), 404

    user = r.json()
    session['uid'] = user['uid']
    session['vip'] = user['subscription'] != None
    r = requests.post(f'http://{BLOCKCHAIN_SERVER}/check-wallet-balance', json={
        'passphrase': user['mnemonic']
    })
    user['balance'] = r.json()['balance']
    del user['mnemonic']

    return jsonify(user), 200


@app.route('/subscribe', methods=['POST'])
def subscribe_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'uid' not in data:
        return jsonify(message='Missing uid'), 400
    if 'uid' not in session or session['uid'] != data['uid']:
        return '', 401

    r = requests.get(f'http://{DB_SERVER}/get-mnemonic?uid={session["uid"]}')
    if r.status_code == 404:
        return jsonify(r.json()), 404

    mnemonic = r.json()['mnemonic']
    r = requests.get(f'http://{BLOCKCHAIN_SERVER}/get-public-address/{mnemonic}')
    address = r.json()['address']

    r = requests.post(f'http://{DB_SERVER}/subscribe', json={ 'uid': session['uid'] })
    if r.status_code != 200:
        return jsonify(message='Internal server error'), 500
    return jsonify(address=address), 200


@app.route('/releases', methods=['GET'])
def get_releases_endpoint():
    r = requests.get(f'http://{DB_SERVER}/releases')
    return jsonify(r.json()), 200


@app.route('/song/<int:mid>', methods=['GET'])
def get_song_endpoint(mid):
    secret = '^mUg0_6o$' if session['vip'] else '5p0Of1N6'
    r = requests.get(f'http://{DB_SERVER}/song/{mid}/{secret}')
    if r.status_code == 400:
        return '', 400
    song = r.json()

    if 'uid' in session:
        r = requests.post(f'http://{DB_SERVER}/add-listener-history', json={
            'uid': session['uid'], 'mid': mid
        })

    return jsonify(song), 200


@app.route('/auctions', methods=['GET'])
def get_auctions_endpoint():
    r = requests.get(f'http://{DB_SERVER}/auctions')
    return jsonify(r.json()), 200


@app.route('/auction/<int:aid>', methods=['GET'])
def get_auction_endpoint(aid):
    r = requests.get(f'http://{DB_SERVER}/auction/{aid}/{session["uid"] if "uid" in session else 0}')
    if r.status_code == 404:
        return '', 404

    return jsonify(r.json()), 200


@app.route('/send-tips', methods=['POST'])
def send_tips_endpoint():
    if 'uid' not in session:
        return jsonify(message='Please sign up for an account before tipping!'), 200
    elif not session['vip']:
        return jsonify(message='You do not have any Algos in your account! Consider becoming a membership to enable the tipping feature.'), 200

    data = request.get_json()
    if data is None:
        return '', 400
    if 'mid' not in data or 'amount' not in data:
        return jsonify(message='Missing data in the request'), 400

    r = requests.get(f'http://{DB_SERVER}/get-mnemonic?uid={session["uid"]}')
    if r.status_code == 404:
        return jsonify(r.json()), 404
    sender = r.json()['mnemonic']

    r = requests.get(f'http://{DB_SERVER}/get-mnemonic?mid={data["mid"]}')
    if r.status_code == 404:
        return jsonify(r.json()), 404
    receiver = r.json()['mnemonic']

    r = requests.post(f'http://{BLOCKCHAIN_SERVER}/send-tips', json={
        'sender': sender, 'receiver': receiver, 'amount': data['amount'],
        'note': 'Tips for <song {}> from <user {}>'.format(data['mid'], session['uid'])
    })
    if r.status_code == 400:
        return jsonify(r.json()) if len(r.text()) > 0 else '', 400
    elif r.status_code == 406:
        return jsonify(r.json()), 406
    elif r.status_code == 500:
        return '', 500
    print(r.json())

    r = requests.post(f'http://{DB_SERVER}/increment-song-tips', json={
        'mid': data['mid'], 'amount': data['amount']
    })

    return jsonify(message='Thank you for tipping the artist!'), 200


@app.route('/upload', methods=['PUT'])
def upload_endpoint():
    if 'uid' not in session:
        return '', 401

    cover, audio = request.files.get('cover'), request.files.get('audio')
    title, dist_type = request.form.get('title'), request.form.get('dtype', type=int)
    start, end = request.form.get('start', type=float), request.form.get('end', type=float)
    if cover is None:
        return jsonify(message='Missing image in the request'), 400
    if audio is None:
        return jsonify(message='Missing audio in the request'), 400
    if cover.filename == '' or audio.filename == '':
        return jsonify(message='No file chosen'), 400
    if title is None:
        return jsonify(message='No title provided'), 400
    if dist_type is None:
        return jsonify(message='No distribution type specified'), 400
    if start is None or end is None:
        return jsonify(message='Demo segement not specified'), 400

    regex = re.compile(r'{}(.*)$'.format(FLASK_STATIC_FOLDER))
    ext = cover.filename.rsplit('.', 1)[-1].lower()
    if ext in ['jpg', 'jpeg', 'png', 'gif']:
        filename = f'{int(datetime.timestamp(datetime.now()))}-{secure_filename(cover.filename)}'
        path = os.path.join(app.config['UPLOAD_FOLER'], filename)
        cover.save(path)
        cover = regex.match(path).group(1)
    else:
        return jsonify(message='File format error'), 400

    ext = audio.filename.rsplit('.', 1)[-1].lower()
    if ext in ['mp3', 'wav']:
        ts = int(datetime.timestamp(datetime.now()))
        filename = secure_filename(audio.filename)
        path = os.path.join(app.config['UPLOAD_FOLER'], f'{ts}-{filename}')
        audio.save(path)
        audio = path
        path = os.path.join(app.config['UPLOAD_FOLER'], f'{ts}-demo-{filename}')
        demo = ffmpeg.input(audio, ss=start, t=end-start)
        demo = ffmpeg.output(demo, path)
        ffmpeg.run(demo)
        audio = regex.match(audio).group(1)
        demo = regex.match(path).group(1)
    else:
        return jsonify(message='File format error'), 400

    r = requests.post(f'http://{DB_SERVER}/create-media', json={
        'title': title, 'full_audio': audio, 'demo_segment': demo,
        'cover': cover, 'dist_type': bool(dist_type), 'uid': session['uid']
    })
    if r.status_code == 400:
        return jsonify(r.json()) if len(r.text) > 0 else '', 400

    return jsonify(status=True, mid=r.json()['mid'], message='Your music has been successfully uploaded to our platform!', redirect='/'), 200


@app.route('/create-auction', methods=['POST'])
def create_auction_endpoint():
    if 'uid' not in session:
        return '', 401

    data = request.get_json()
    if data is None or 'title' not in data:
        return '', 400
    asset_name = secure_filename(data['title'])
    del data['title']
    data['uid'] = session['uid']
    try:
        startTimestamp = data['start']
        endTimestamp = data['end']
        data['start'] = datetime.fromtimestamp(data['start']).strftime('%Y-%m-%d %H:%M:%S')
        data['end'] = datetime.fromtimestamp(data['end']).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return jsonify(message='Start and end time needs to be Unix timestamp!'), 400

    r = requests.post(f'http://{DB_SERVER}/create-auction', json=data)
    if r.status_code == 400:
        return jsonify(r.json()), 400
    aid = r.json()['aid']

    # get the artist's mnemonic
    r = requests.get(f'http://{DB_SERVER}/get-mnemonic?uid={session["uid"]}')
    if r.status_code == 400:
        return '', 400
    elif r.status_code == 404:
        return jsonify(r.json()), 404
    mnemonic = r.json()['mnemonic']

    r = requests.post(f'http://{BLOCKCHAIN_SERVER}/create-asset', json={
        'passphrase': mnemonic, 'asset_name': asset_name,
        'auction_page': f'/view/auction/{aid}', 'amount': data['amount'],
        'note': '<Auction {}> by <User {}>'.format(aid, session['uid'])
    })
    if r.status_code == 400 or r.status_code == 500:
        return jsonify(r.json()), r.status_code
    print(r.json())
    asset_id = r.json()['asset_id']

    r = requests.put(f'http://{BLOCKCHAIN_SERVER}/create-smart-contract', json={
        'passphrase': mnemonic, 'assetId': asset_id, 'amount': data['amount'],
        'start': startTimestamp, 'end': endTimestamp, 'minBid': data['minBid']
    })
    if r.status_code != 201:
        return jsonify(r.json()), r.status_code
    print(r.json())
    contract_id = r.json()['contract_id']

    r = requests.post(f'http://{DB_SERVER}/update-auction', json={
        'aid': aid, 'assetId': asset_id, 'contractId': contract_id
    })
    if r.status_code != 200:
        return jsonify(r.json()) if len(r.text()) > 0 else '', r.status_code

    return jsonify(status=True, message='Your auction has been successfully created!', redirect='#/auction'), 201


@app.route('/submit-bid', methods=['POST'])
def submit_bid_endpoint():
    if 'uid' not in session:
        return jsonify(message='Please login to participate in the auction!'), 401
    if 'vip' not in session:
        return jsonify(message='You do not have any Algos in your account! Consider becoming a membership to enable the bidding feature.'), 401

    data = request.get_json()
    if data is None:
        return '', 400
    if 'aid' not in data:
        return jsonify(message='Missing aid in the request'), 400
    if 'bid' not in data:
        return jsonify(message='Missing bid in the request'), 400

    r = requests.get(f'http://{DB_SERVER}/get-bids/{data["aid"]}')
    if r.status_code == 404:
        return jsonify(message='Auction {} does not exist!'.format(data['aid'])), 404
    auction = r.json()

    if datetime.utcnow() < datetime.strptime(auction['start'], '%Y-%m-%dT%H:%M:%S'):
        return jsonify(message='The auction has not started yet'), 403
    if session['uid'] == auction['uid']:
        return jsonify(message='You cannot participate in your own auction!'), 400
    if data['bid'] < auction['minBid']:
        return jsonify(message='You must enter a bid greater than or equal to the minimum bid set by the artist!'), 400

    r = requests.get(f'http://{DB_SERVER}/get-mnemonic?uid={session["uid"]}')
    if r.status_code != 200:
        return jsonify(message='Server error'), r.status_code
    mnemonic = r.json()['mnemonic']

    r = requests.post(f'http://{BLOCKCHAIN_SERVER}/opt-in-contract', json={
        'passphrase': mnemonic, 'contract_id': auction['contractId']
    })
    if r.status_code != 200:
        if len(r.text()) > 0: print(r.json()['message'])
        return jsonify(message='Failed to opt in the smart contract! Please check if you have enough Algos in your balance.'), r.status_code

    r = requests.post(f'http://{BLOCKCHAIN_SERVER}/participate-in-auction', json={
        'passphrase': mnemonic, 'bid': data['bid'], 'contract_id': auction['contractId'],
        'note': '<User {}> bade {} Algos in <Auction {}>'.format(session['uid'], data['bid'], data['aid'])
    })
    if r.status_code == 406:
        return jsonify(r.json()), 406
    if r.status_code == 500:
        print(r.json()['message'])
        return jsonify(message='Request failed to satisfy the smart contract! Please check if your bid is higher than the current lowest bid.'), 400

    auction['bids'].sort(key=lambda x: x['bid'], reverse=True)
    if len(auction['bids']) >= auction['amount']: # kick someone out
        p = auction['bids'].pop()

        r = requests.get(f'http://{DB_SERVER}/get-mnemonic?uid={p["uid"]}')
        if r.status_code != 200:
            return jsonify(message='Server error'), r.status_code
        mnemonic = r.json()['mnemonic']

        r = requests.post(f'http://{BLOCKCHAIN_SERVER}/refund', json={
            'passphrase': mnemonic, 'amount': p['bid'], 'contract_id': auction['contractId'],
            'note': '<User {}> was kicked out of <Auction {}> with bid {} Algos'.format(p['uid'], data['aid'], p['bid'])
        })
        if r.status_code == 500:
            print(r.json()['message'])
            return jsonify(r.json()), 500

        r = requests.delete(f'http://{DB_SERVER}/delete-bid', json={
            'aid': data['aid'], 'uid': p['uid']
        })

    auction['bids'].append({ 'uid': session['uid'], 'bid': data['bid'] })
    auction['bids'].sort(key=lambda x: x['bid'], reverse=True)
    r = requests.post(f'http://{BLOCKCHAIN_SERVER}/update-lowest-bid', json={
        'bid': auction['bids'][-1]['bid'], 'contract_id': auction['contractId']
    })
    if r.status_code != 200:
        return jsonify(r.json()) if len(r.text()) > 0 else '', r.status_code

    r = requests.post(f'http://{DB_SERVER}/create-bid', json={
        'bid': data['bid'], 'uid': session['uid'], 'aid': data['aid']
    })

    return jsonify(status=True, message='Thank you for your participation! We wish you could get your position locked.'), 200


@app.route('/complete-auction', methods=['POST'])
def complete_auction_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'aid' not in data:
        return jsonify(message='Missing aid in the request'), 400

    r = requests.get(f'http://{DB_SERVER}/get-bids/{data["aid"]}')
    if r.status_code == 404:
        return jsonify(message='Auction {} does not exist!'.format(data['aid'])), 404
    auction = r.json()

    if datetime.utcnow() < datetime.strptime(auction['end'], '%Y-%m-%dT%H:%M:%S'):
        return jsonify(message='The auction has not finished yet'), 403
    if auction['contractId'] is None:
        return jsonify(message='<Auction {}> has already wrapped up.'.format(data['aid'])), 200

    r = requests.get(f'http://{DB_SERVER}/get-mnemonic?uid={auction["uid"]}')
    if r.status_code != 200:
        return jsonify(message='Server error'), r.status_code
    artist = r.json()['mnemonic']

    for participant in auction['bids']:
        r = requests.get(f'http://{DB_SERVER}/get-mnemonic?uid={participant["uid"]}')
        if r.status_code != 200:
            return jsonify(message='Server error'), r.status_code
        mnemonic = r.json()['mnemonic']

        r = requests.post(f'http://{BLOCKCHAIN_SERVER}/win-auction', json={
            'passphrase': mnemonic, 'owner': artist, 'bid': participant['bid'],
            'asset_id': auction['assetId'], 'contract_id': auction['contractId'],
            'note': 'Earned {} Algos from selling <Asset {}> to <User {}> in <Auction {}>'.format(participant['bid'] * 0.9, auction['assetId'], participant['uid'], data['aid'])
        })
        if r.status_code == 400:
            return jsonify(r.json()) if len(r.text()) > 0 else '', 400
        elif r.status_code == 500:
            print(r.json()['message'])
            return jsonify(message='Completion transaction failed for <User {}>'.format(participant['uid'])), 500

        r = requests.post(f'http://{DB_SERVER}/create-ownership', json={
            'uid': participant['uid'], 'aid': data['aid'], 'mid': auction['mid']
        })

    r = requests.delete(f'http://{BLOCKCHAIN_SERVER}/delete-contract', json={
        'contract_id': auction['contractId']
    })
    if r.status_code == 400:
        return jsonify(r.json()) if len(r.text()) > 0 else '', 400
    elif r.status_code == 500:
        print(r.json()['message'])
        return jsonify(message='Server error'), 500

    r = requests.post(f'http://{DB_SERVER}/update-auction', json={
        'aid': data['aid'], 'contractId': None,
        'sold': len(auction['bids']), 'earnings': sum(map(lambda p: p['bid'], auction['bids'])) * 0.9
    })
    print(r.json())

    return '', 200
