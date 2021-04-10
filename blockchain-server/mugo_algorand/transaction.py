from algosdk.future.transaction import PaymentTxn
from .util import wait_for_confirmation
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
