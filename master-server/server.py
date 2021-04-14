from .config import *
import os, re, requests, ffmpeg
from datetime import datetime
from flask import Flask, request, session, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/', static_folder=FLASK_STATIC_FOLDER, root_path=os.path.dirname(os.path.abspath(__file__)))
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['UPLOAD_FOLER'] = FLASK_UPLOAD_FOLDER


@app.route('/', methods=['GET'])
def on_start():
    requests.put(f'http://{DB_SERVER}/init')
    return app.send_static_file('index.html'), 200


@app.route('/signup', methods=['POST'])
def signup_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    # TODO: password hash etc.
    r = requests.put(f'http://{BLOCKCHAIN_SERVER}/create-wallet')
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

    return jsonify(status=True, mid=r.json()['mid']), 200
