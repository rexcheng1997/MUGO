from algosdk import account, mnemonic

def create_wallet():
    """
    Creates an Algorand wallet and returns the mnemonic of the new wallet.
    @returns a string of the 25-word passphrase
    """
    private_key, account_address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    return passphrase

def get_wallet_key_pairs(passphrase):
    """
    @params{passphrase} - 25-word mnemonic string
    Returns a dictionary containing the public key (account address) and private key of the wallet.
    @returns {
        'public_key': string,
        'private_key': string
    }
    """
    return {
        'public_key': mnemonic.to_public_key(passphrase),
        'private_key': mnemonic.to_private_key(passphrase)
    }
