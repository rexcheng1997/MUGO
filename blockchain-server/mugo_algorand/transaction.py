from algosdk.future.transaction import \
    calculate_group_id, \
    StateSchema, \
    OnComplete, \
    PaymentTxn, \
    AssetConfigTxn, \
    AssetTransferTxn, \
    ApplicationCreateTxn, \
    ApplicationOptInTxn, \
    ApplicationNoOpTxn, \
    ApplicationCloseOutTxn, \
    ApplicationDeleteTxn

from .util import *
import json

def one_way_transaction(algod_client, sender, receiver, amount, note='', sign=True):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the sender
                    - { 'public_key': string, 'private_key': string }
    @params{receiver} - a string of the public key (account address) of the receiver
    @params{amount} - an int of transaction amount in microAlgos
    @params{note} OPTIONAL - a string of note to put in the transaction
    @params{sign} OPTIONAL - boolean whether or not to sign and send the transaction
    Makes a transaction and returns the information of the transaction.
    @returns {
        'status': boolean,
        'txid': string,
        'info': json string containing the transaction information if status is True else a string of error message
    } if sign else {
        'sender': a dictionary containing the public/private key of the holder,
        'txn': unsigned transaction
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000
    unsigned_txn = PaymentTxn(sender['public_key'], params, receiver, amount, None, note.encode())
    if not sign:
        return { 'sender': sender, 'txn': unsigned_txn }

    signed_txn = unsigned_txn.sign(sender['private_key'])
    txid = algod_client.send_transaction(signed_txn)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'txid': txid,
        'info': json.dumps(confirmed_txn)
    }

def create_asset(algod_client, holder, name, url, amount, note=''):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{holder} - a dictionary containing the public/private key of the holder
                    - { 'public_key': string, 'private_key': string }
    @params{name} - a string of asset name
    @params{url} - a string of the url of the targeted auction page
    @params{amount} - an int of the number of assets to create
    @params{note} OPTIONAL - a string of note to put in the transaction
    Creates an asset with the given amount as NFTs to sell.
    @returns {
        'status': boolean,
        'asset_id': int,
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000
    unsigned_txn = AssetConfigTxn(
        sender=holder['public_key'], sp=params, total=amount, default_frozen=False,
        unit_name='NFT', asset_name=name, manager=holder['public_key'],
        reserve=holder['public_key'], freeze=holder['public_key'], clawback=holder['public_key'],
        url=url, decimals=0)
    signed_txn = unsigned_txn.sign(holder['private_key'])
    txid = algod_client.send_transaction(signed_txn)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
        print_created_asset(algod_client, holder['public_key'], confirmed_txn['asset-index'])
        print_asset_holding(algod_client, holder['public_key'], confirmed_txn['asset-index'])
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'asset_id': confirmed_txn['asset-index'],
        'info': json.dumps(confirmed_txn)
    }

def opt_in_asset(algod_client, sender, asset_id):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the holder
                    - { 'public_key': string, 'private_key': string }
    @params{asset_id} - int asset id
    Opts in an asset with the asset id.
    @returns {
        'status': boolean,
        'txid': string
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    account_info = algod_client.account_info(sender['public_key'])
    hold = False
    for scrutinized_asset in account_info['assets']:
        if scrutinized_asset['asset-id'] == asset_id:
            hold = True
            break
    if not hold:
        unsigned_txn = AssetTransferTxn(sender=sender['public_key'], sp=params, receiver=sender['public_key'], amt=0, index=asset_id)
        signed_txn = unsigned_txn.sign(sender['private_key'])
        txid = algod_client.send_transaction(signed_txn)
        print('Pending transaction with id: {}'.format(txid))
        try:
            confirmed_txn = wait_for_confirmation(algod_client, txid)
        except Exception as err:
            print(err)
            return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
        return {
            'status': True,
            'txid': txid,
            'info': json.dumps(confirmed_txn)
        }
    return {
        'status': True,
        'txid': '',
        'info': ''
    }

def transfer_asset(algod_client, sender, receiver, asset_id, sign=True):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the holder
                    - { 'public_key': string, 'private_key': string }
    @params{receiver} - a string of the public key (account address) of the receiver
    @params{asset_id} - int asset id
    @params{sign} OPTIONAL - boolean whether or not to sign and send the transaction
    Transfer 1 asset (NFT) from sender to receiver.
    @returns {
        'status': boolean,
        'txid': string
        'info': json string containing the transaction information if status is True else a string of error message
    } if sign else {
        'sender': a dictionary containing the public/private key of the holder,
        'txn': unsigned transaction
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    unsigned_txn = AssetTransferTxn(sender=sender['public_key'], sp=params, receiver=receiver, amt=1, index=asset_id)
    if not sign:
        return { 'sender': sender, 'txn': unsigned_txn }
    signed_txn = unsigned_txn.sign(sender['private_key'])
    txid = algod_client.send_transaction(signed_txn)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'txid': txid,
        'info': json.dumps(confirmed_txn)
    }


def send_single_transaction(algod_client, txn):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{txn} - a list of transaction objects as dictionary in the following format
                       - {
                            'sender': a dictionary containing the public/private key of the holder,
                            'txn': unsigned transaction
                         }
    Sends the transaction.
    @returns {
        'status': boolean,
        'txid': string,
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    signed_txn = txn['txn'].sign(txn['sender']['private_key'])
    txid = algod_client.send_transaction(signed_txn)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'txid': txid,
        'info': json.dumps(confirmed_txn)
    }

def send_grouped_transactions(algod_client, txn_group):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{txn_group} - a list of transaction objects as dictionary in the following format
                       - {
                            'sender': a dictionary containing the public/private key of the holder,
                            'txn': unsigned transaction
                         }
    Groups the transactions and sends them.
    @returns {
        'status': boolean,
        'txid': string,
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    gid = calculate_group_id([t['txn'] for t in txn_group])
    signed_group = []
    for t in txn_group:
        t['txn'].group = gid
        signed_txn = t['txn'].sign(t['sender']['private_key'])
        signed_group.append(signed_txn)
    txid = algod_client.send_transactions(signed_group)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'txid': txid,
        'info': json.dumps(confirmed_txn)
    }

def create_contract_transaction(algod_client, sender, approval_program, clear_program, schema, args):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the holder
                    - { 'public_key': string, 'private_key': string }
    @params{approval_program} - compiled TEAL smart contract approval program, obtained from compile_smart_contract
    @params{clear_program} - compiled TEAL smart contract clear program, obtained from compile_smart_contract
    @params{schema} - a dictionary containing the StateSchema of the smart contract
                    - {
                        'gint': number of ints to store in the global state,
                        'gbyte': number of bytes to store in the global state,
                        'lint': number of ints to store in the local state,
                        'lbyte': number of bytes to store in the local state
                      }
    @params{args} - a list of arguments passed to the create transaction, matching the order in the smart contract
    Creates a stateful smart contract for an auction.
    @returns {
        'status': boolean,
        'contract_id': int,
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    global_schema = StateSchema(schema['gint'], schema['gbyte'])
    local_schema = StateSchema(schema['lint'], schema['lbyte'])

    unsigned_txn = ApplicationCreateTxn(sender['public_key'], params, OnComplete.NoOpOC.real, approval_program, clear_program, global_schema, local_schema, args)
    signed_txn = unsigned_txn.sign(sender['private_key'])
    txid = algod_client.send_transaction(signed_txn)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'contract_id': confirmed_txn['application-index'],
        'info': json.dumps(confirmed_txn)
    }

def opt_in_contract_transaction(algod_client, sender, contract_id):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the holder
                    - { 'public_key': string, 'private_key': string }
    @params{contract_id} - smart contract id
    Opt in the sender to the smart contract with contract_id.
    @returns {
        'status': boolean,
        'txid': string,
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    unsigned_txn = ApplicationOptInTxn(sender['public_key'], params, contract_id)
    signed_txn = unsigned_txn.sign(sender['private_key'])
    txid = algod_client.send_transaction(signed_txn)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'txid': txid,
        'info': json.dumps(confirmed_txn)
    }

def call_contract_transaction(algod_client, sender, contract_id, args):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the holder
                    - { 'public_key': string, 'private_key': string }
    @params{contract_id} - smart contract id
    @params{args} - a list of arguments passed to the create transaction, matching the order in the smart contract
    Calls the smart contract with contract_id with args.
    @returns {
        'sender': a dictionary containing the public/private key of the holder,
        'txn': unsigned transaction
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    unsigned_txn = ApplicationNoOpTxn(sender['public_key'], params, contract_id, args)
    return {
        'sender': sender,
        'txn': unsigned_txn
    }

def leave_contract_transaction(algod_client, sender, contract_id):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the holder
                    - { 'public_key': string, 'private_key': string }
    @params{contract_id} - smart contract id
    Closes out the contract, removing the local state of contract_id from sender's account.
    @returns {
        'status': boolean,
        'txid': string,
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    unsigned_txn = ApplicationCloseOutTxn(sender['public_key'], params, contract_id)
    signed_txn = unsigned_txn.sign(sender['private_key'])
    txid = algod_client.send_transaction(signed_txn)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'txid': txid,
        'info': json.dumps(confirmed_txn)
    }

def delete_contract_transaction(algod_client, sender, contract_id):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the holder
                    - { 'public_key': string, 'private_key': string }
    @params{contract_id} - smart contract id
    Deletes the contract with contract_id.
    @returns {
        'status': boolean,
        'txid': string,
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    unsigned_txn = ApplicationDeleteTxn(sender['public_key'], params, contract_id)
    signed_txn = unsigned_txn.sign(sender['private_key'])
    txid = algod_client.send_transaction(signed_txn)
    print('Pending transaction with id: {}'.format(txid))
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return { 'status': False, 'txid': txid, 'info': getattr(err, 'message', str(err)) }
    return {
        'status': True,
        'txid': txid,
        'info': json.dumps(confirmed_txn)
    }
