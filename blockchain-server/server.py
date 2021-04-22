import os
from flask import Flask, request, jsonify
from algosdk.v2client import algod
from algosdk import encoding, error
from mugo_algorand.wallet import *
from mugo_algorand.transaction import *
from mugo_algorand.contract import compile_smart_contract
from mugo_algorand.util import read_local_state, read_global_state

app = Flask(__name__)
algod_client = algod.AlgodClient(
    algod_token='',
    algod_address='https://api.testnet.algoexplorer.io',
    headers={ 'User-Agent': 'DoYouLoveMe?' })
ESCROW_MNEMONIC = os.getenv('ESCROW_MNEMONIC', '')


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
    if msg is not None:
        return jsonify(message=msg), 400
    if data['sender'] == data['receiver']:
        return '', 200

    sender_wallet = get_wallet_key_pairs(data['sender'])
    receiver_wallet = get_wallet_key_pairs(data['receiver'])
    sender_account_info = algod_client.account_info(sender_wallet['public_key'])
    sender_balance = sender_account_info.get('amount')

    if sender_balance < data['amount'] * 10 ** 6 + 1000: # 1000 is the gas fee
        return jsonify(message='You do not have {} Algos in your balance!'.format(data['amount'] + 0.001)), 406

    txn = one_way_transaction(algod_client, sender_wallet, receiver_wallet['public_key'], int(data['amount'] * (10 ** 6)), data.get('note', ''))
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    return txn['info'], 200


@app.route('/create-asset', methods=['POST'])
def create_asset_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    msg = None
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
    if msg is not None:
        return jsonify(message=msg), 400

    wallet = get_wallet_key_pairs(data['passphrase'])
    txn = create_asset(algod_client, wallet, data['asset_name'], data['auction_page'], data['amount'], data['note'])
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    del txn['status']
    return jsonify(txn), 201


@app.route('/create-smart-contract', methods=['PUT'])
def create_smart_contract_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    msg = None
    if 'passphrase' not in data:
        msg = 'Passphrase missing'
    elif 'assetId' not in data:
        msg = 'Asset ID missing'
    elif 'amount' not in data:
        msg = 'Amount missing'
    elif 'start' not in data or 'end' not in data:
        msg = 'Start or end time missing'
    elif 'minBid' not in data:
        msg = 'Minimum bid missing'
    if msg is not None:
        return jsonify(message=msg), 400

    approval_program, clear_program = compile_smart_contract(algod_client)

    sender_account = get_wallet_key_pairs(ESCROW_MNEMONIC)
    state_schema = {
        'gint': 7, 'gbyte': 3,
        'lint': 1, 'lbyte': 0
    }
    args = [
        data['assetId'].to_bytes(8, 'big'),
        data['start'].to_bytes(8, 'big'),
        data['end'].to_bytes(8, 'big'),
        int(data['minBid'] * 10 ** 6).to_bytes(8, 'big'),
        data['amount'].to_bytes(8, 'big'),
        encoding.decode_address(get_wallet_key_pairs(data['passphrase'])['public_key'])
    ]

    txn = create_contract_transaction(algod_client, sender_account, approval_program, clear_program, state_schema, args)
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    del txn['status']
    # check if correct values are stored in the contract's global state
    read_global_state(algod_client, sender_account['public_key'], txn['contract_id'])

    return jsonify(txn), 201


@app.route('/opt-in-contract', methods=['POST'])
def opt_in_contract_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'passphrase' not in data:
        return jsonify(message='Passphrase missing'), 400
    if 'contract_id' not in data:
        return jsonify(message='Contract ID missing'), 400

    sender_account = get_wallet_key_pairs(data['passphrase'])
    try:
        txn = opt_in_contract_transaction(algod_client, sender_account, data['contract_id'])
        if not txn['status']:
            return jsonify(message=txn['info']), 500
        del txn['status']
        return jsonify(txn), 200
    except error.AlgodHTTPError as e:
        status_code = 500
        if 'already opted in' in str(e):
            status_code = 200
        return jsonify(message=repr(e)), status_code


@app.route('/participate-in-auction', methods=['POST'])
def participate_in_auction_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    msg = None
    if 'passphrase' not in data:
        msg = 'Passphrase missing'
    elif 'bid' not in data:
        msg = 'Bid missing'
    elif 'contract_id' not in data:
        msg = 'Contract ID missing'
    if msg is not None:
        return jsonify(message=msg), 400

    participant_account = get_wallet_key_pairs(data['passphrase'])
    participant_account_info = algod_client.account_info(participant_account['public_key'])
    balance = participant_account_info.get('amount')

    if balance < data['bid'] * 10 ** 6 + 2000:
        return jsonify(message='You do not have {} Algos in your balance!'.format(data['bid'] + 0.002)), 406

    call_contract = call_contract_transaction(algod_client, participant_account, data['contract_id'], [str.encode('Bid')])
    pay_bid = one_way_transaction(algod_client, participant_account, get_wallet_key_pairs(ESCROW_MNEMONIC)['public_key'], int(data['bid'] * 10 ** 6), data.get('note', ''), False)

    txn = send_grouped_transactions(algod_client, [call_contract, pay_bid])
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    del txn['status']
    # check if the bid was recorded in the participant's local state
    read_local_state(algod_client, participant_account['public_key'], data['contract_id'])

    return jsonify(txn), 200


@app.route('/update-lowest-bid', methods=['POST'])
def update_lowest_bid_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'bid' not in data:
        return jsonify(message='Lowest bid missing'), 400
    if 'contract_id' not in data:
        return jsonify(message='Contract ID missing'), 400

    escrow_account = get_wallet_key_pairs(ESCROW_MNEMONIC)

    call_contract = call_contract_transaction(algod_client, escrow_account, data['contract_id'], [str.encode('Update'), int(data['bid'] * 10 ** 6).to_bytes(8, 'big')])
    txn = send_single_transaction(algod_client, call_contract)
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    del txn['status']
    # check if the lowest bid stored in the contract's global state was updated
    read_global_state(algod_client, escrow_account['public_key'], data['contract_id'])

    return jsonify(txn), 200


@app.route('/refund', methods=['POST'])
def refund_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'passphrase' not in data:
        return jsonify(message='Passphrase missing'), 400
    if 'amount' not in data:
        return jsonify(message='Refund amount missing'), 400
    if 'contract_id' not in data:
        return jsonify(message='Contract ID missing'), 400

    participant_account = get_wallet_key_pairs(data['passphrase'])
    escrow_account = get_wallet_key_pairs(ESCROW_MNEMONIC)

    call_contract = call_contract_transaction(algod_client, participant_account, data['contract_id'], [str.encode('Refund')])
    refund_bid = one_way_transaction(algod_client, escrow_account, participant_account['public_key'], int(data['amount'] * 10 ** 6) - 1000, data.get('note', ''), False)

    txn = send_grouped_transactions(algod_client, [call_contract, refund_bid])
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    del txn['status']

    close_out = leave_contract_transaction(algod_client, participant_account, data['contract_id'])
    if not close_out['status']:
        return jsonify(message=close_out['info']), 500

    return jsonify(txn), 200


@app.route('/win-auction', methods=['POST'])
def win_auction_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    msg = None
    if 'passphrase' not in data:
        msg = 'Passphrase missing'
    elif 'owner' not in data:
        msg = 'Artist passphrase missing'
    elif 'bid' not in data:
        msg = 'Bid missing'
    elif 'asset_id' not in data:
        msg = 'Asset ID missing'
    elif 'contract_id' not in data:
        msg = 'Contract ID missing'
    if msg is not None:
        return jsonify(message=msg), 400

    participant_account = get_wallet_key_pairs(data['passphrase'])
    artist_account = get_wallet_key_pairs(data['owner'])
    escrow_account = get_wallet_key_pairs(ESCROW_MNEMONIC)

    opt_in = opt_in_asset(algod_client, participant_account, data['asset_id'])
    if not opt_in['status']:
        return jsonify(message=opt_in['info']), 500

    call_contract = call_contract_transaction(algod_client, participant_account, data['contract_id'], [str.encode('Win')])
    pay_artist = one_way_transaction(algod_client, escrow_account, artist_account['public_key'], int(data['bid'] * 10 ** 6 * 0.9), data.get('note', ''), False)
    asset_transfer = transfer_asset(algod_client, artist_account, participant_account['public_key'], data['asset_id'], False)

    txn = send_grouped_transactions(algod_client, [call_contract, pay_artist, asset_transfer])
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    del txn['status']

    close_out = leave_contract_transaction(algod_client, participant_account, data['contract_id'])
    if not close_out['status']:
        return jsonify(message=close_out['info']), 500

    return jsonify(txn), 200


@app.route('/delete-contract', methods=['DELETE'])
def delete_contract_endpoint():
    data = request.get_json()
    if data is None:
        return '', 400
    if 'contract_id' not in data:
        return jsonify(message='Contract ID missing'), 400

    escrow_account = get_wallet_key_pairs(ESCROW_MNEMONIC)

    txn = delete_contract_transaction(algod_client, escrow_account, data['contract_id'])
    if not txn['status']:
        return jsonify(message=txn['info']), 500
    del txn['status']

    return jsonify(txn), 200
