import os

FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', '6$7c8f0e_o9T!z')
FLASK_STATIC_FOLDER = os.getenv('FLASK_STATIC_FOLDER', '../static')
DB_SERVER_HOST = os.getenv('DB_SERVER', 'localhost')
DB_SERVER_PORT = '5001'
DB_SERVER = ':'.join([DB_SERVER_HOST, DB_SERVER_PORT])
BLOCKCHAIN_SERVER_HOST = os.getenv('BLOCKCHAIN_SERVER', 'localhost')
BLOCKCHAIN_SERVER_PORT = '5000'
BLOCKCHAIN_SERVER = ':'.join([BLOCKCHAIN_SERVER_HOST, BLOCKCHAIN_SERVER_PORT])

import requests
from flask import Flask, request, session, jsonify

app = Flask(__name__, static_url_path='/', static_folder=FLASK_STATIC_FOLDER, root_path=os.path.dirname(os.path.abspath(__file__)))
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

@app.route('/', methods=['GET'])
def on_start():
    requests.put(f'http://{DB_SERVER}/init')
    return app.send_static_file('index.html'), 200


@app.route('/signup', methods=['POST'])
def signup_endpoint():
    data = request.get_json()
    if data == None:
        return '', 400
    # TODO: password hash etc.
    # r = requests.put(f'http://{BLOCKCHAIN_SERVER}/create-wallet')
    # data['mnemonic'] = r.json()['mnemonic']
    data['mnemonic'] = 'aaa bbb ccc'
    r = requests.post(f'http://{DB_SERVER}/create-user', json=data)
    if r.status_code == 400:
        return jsonify(r.json()) if len(r.text) > 0 else '', 400
    return jsonify(status=True), 200
