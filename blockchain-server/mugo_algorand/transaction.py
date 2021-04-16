from algosdk.future.transaction import PaymentTxn, AssetConfigTxn
from .util import *
import json

def one_way_transaction(algod_client, sender, receiver, amount, note=''):
    """
    @params{algod_client} - AlgodClient instance created by calling algod.AlgodClient
    @params{sender} - a dictionary containing the public/private key of the sender
                    - { 'public_key': string, 'private_key': string }
    @params{receiver} - a string of the public key (account address) of the receiver
    @params{amount} - an int of transaction amount in microAlgos
    @params{note} OPTIONAL - a string of note to put in the transaction
    Makes a transaction and returns the information of the transaction.
    @returns {
        'status': boolean,
        'txid': string,
        'info': json string containing the transaction information if status is True else a string of error message
    }
    """
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000
    unsigned_txn = PaymentTxn(sender['public_key'], params, receiver, amount, None, note.encode())
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
