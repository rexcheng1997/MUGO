from flask import Flask, request, jsonify
from algosdk.v2client import algod
from mugo_algorand.wallet import *
from mugo_algorand.transaction import *

app = Flask(__name__)
algod_client = algod.AlgodClient(
    algod_token='',
    algod_address='https://api.testnet.algoexplorer.io',
    headers={ 'User-Agent': 'DoYouLoveMe?' })


@app.route('/create-wallet', methods=['PUT'])
def create_wallet_endpoint():
    passphrase = create_wallet()
    return jsonify(mnemonic=passphrase), 201


@app.route('/get-public-address/<string:passphrase>', methods=['GET'])
def get_public_address_endpoint(passphrase):
    wallet = get_wallet_key_pairs(passphrase)
    return jsonify(address=wallet['public_key']), 200


@app.route('/check-wallet-balance', methods=['POST'])
def check_wallet_balance_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'passphrase' not in data:
        return jsonify(message='Passphrase missing'), 400

    wallet = get_wallet_key_pairs(data['passphrase'])
    account_info = algod_client.account_info(wallet['public_key'])
    balance = account_info.get('amount')
    return jsonify(balance=balance / (10 ** 6)), 200


@app.route('/create-asset', methods=['POST'])
def create_asset_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    msg = ''
    if 'passphrase' not in data:
        msg = 'Passphrase missing'
    elif 'asset_name' not in data:
        msg = 'Asset name missing'
    elif 'auction_page' not in data:
        msg = 'Auction page url missing'
    elif 'amount' not in data:
        msg = 'Amount missing'
    elif 'note' not in data:
        msg = 'Note missing'
    if len(msg) > 0:
        return jsonify(message=msg), 400

    wallet = get_wallet_key_pairs(data['passphrase'])
    txn = create_asset(algod_client, wallet, data['asset_name'], data['auction_page'], data['amount'], data['note'])
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    del txn['status']
    return jsonify(txn), 201


@app.route('/send-tips', methods=['POST'])
def send_tips_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    msg = None
    if 'sender' not in data:
        msg = 'Sender missing'
    elif 'receiver' not in data:
        msg = 'Receiver missing'
    elif 'amount' not in data:
        msg = 'Amount missing'
    if msg != None:
        return jsonify(message=msg), 400
    if data['sender'] == data['receiver']:
        return '', 200

    sender_wallet = get_wallet_key_pairs(data['sender'])
    receiver_wallet = get_wallet_key_pairs(data['receiver'])
    sender_account_info = algod_client.account_info(sender_wallet['public_key'])
    sender_balance = sender_account_info.get('amount')

    if sender_balance < data['amount'] * (10 ** 6) + 1000: # 1000 is the gas fee
        return jsonify(message='You do not have {} algos in your balance!'.format(data['amount'])), 406

    txn = one_way_transaction(algod_client, sender_wallet, receiver_wallet['public_key'], int(data['amount'] * (10 ** 6)), data.get('note', ''))
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    return txn['info'], 200
