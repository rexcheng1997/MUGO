from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn
import json

def wait_for_confirmation(client, txid, timeout=5):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    current = start = client.status()['last-round'] + 1;
    while current < start + timeout:
        try:
            pending_txn = client.pending_transaction_info(txid)
        except:
            raise Exception(f'Failed to get pending tx info with id {txid}')
        if pending_txn.get('confirmed-round', 0) > 0:
            return pending_txn
        elif pending_txn['pool-error']:
            raise Exception(f'Pool error: {pending_txn["pool-error"]}')
        client.status_after_block(current)
        current += 1
    raise Exception(f'Pending tx not found in timeout rounds, timeout value = : {timeout}')

def print_created_asset(client, account, asset_id):
    """
    Utility function used to print created asset for account and asset_id
    """
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = asset_id)
    # then use 'account_info['created-assets'][0] to get info on the created asset
    account_info = client.account_info(account)
    idx = 0;
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1
        if (scrutinized_asset['index'] == asset_id):
            print("Asset ID: {}".format(scrutinized_asset['index']))
            print(json.dumps(my_account_info['params'], indent=4))
            break

def print_asset_holding(client, account, asset_id):
    """
    Utility function used to print asset holding for account and asset_id
    """
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = asset_id)
    # then loop thru the accounts returned and match the account you are looking for
    account_info = client.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1
        if (scrutinized_asset['asset-id'] == asset_id):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break

def read_local_state(client, addr, app_id):
    """
    Utility function to read user local state of contract app_id for user with addr
    """
    results = client.account_info(addr)
    local_state = results['apps-local-state'][0]
    for index in local_state :
        if local_state[index] == app_id :
            print(f'local_state of account {addr} for app_id {app_id}: ', local_state['key-value'])

def read_global_state(client, addr, app_id):
    """
    Utility function to read contract global state given the creator with addr
    """
    results = client.account_info(addr)
    apps_created = results['created-apps']
    for app in apps_created :
        if app['id'] == app_id :
            print(f'global_state for app_id {app_id}: ', app['params']['global-state'])
