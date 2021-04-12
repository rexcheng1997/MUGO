# Endpoints Documentation for server.py
All endpoints, unless specified, expect json input and return json. The spec is formatted in key-value pairs.

*Note: More endpoints will be added*

### /create-wallet
Creates an Algo wallet
- Method: **PUT**

- Input: N/A

- Output: `201 Created`
	- mnemonic (str): The 25-word mnemonic of the created wallet


### /check-wallet-balance
Returns the balance of a wallet
- Method: **POST**

- Input:

	- passphrase (str): the 25-word mnemonic for which the balance will be checked


- Output: `200 OK`

 	- balance (float): the balance associated with the given wallet in Algos

*Note: This method will be modified later to have an additional return value (earnings)*

### /send-tips
Sends a customized amount of tip to an artist/music producer
- Method: **POST**

- Input:
	- sender (str): the 25-word mnemonic of the sender's wallet

	- receiver (str): the 25-word mnemonic of the receiver's wallet

	- amount (float): tip amount in Algos

	- note (str) OPTIONAL: a note to bind with the transaction (keep it short!)

- Output:

	If the request succeeds, `200 OK`

	json of the transaction details (see the sample below)

	If the request fails, `406 Not Acceptable` / `500 Internal Server Error`
	- message (str): error message indicating why the transaction failed

*Sample output for `/send-tips`:*
```json
{
	"confirmed-round": 13343258,
	"pool-error": "",
	"sender-rewards": 21084,
	"txn": {
		"sig": "KQ9rRCEnPw6CeopJnkoFcmAF8/0RCP16ddDLso3cvqht5LEbh0EUEA+Mszctte0NkcX2asslg03zkUbGeVQABA==",
		"txn": {
			"amt": 1420000,
			"fee": 1000,
			"fv": 13343256,
			"gen": "testnet-v1.0",
			"gh": "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI=",
			"lv": 13344256,
			"note": "TVVHTzogVGVzdCBzZW5kLXRpcHMgZW5kcG9pbnQ=",
			"rcv": "RHWYN3ZBZJ7YAIEQWL3M3CTCDJE5W4OPSASHJQZZSE5TUDQJUF2IAWJFLY",
			"snd": "PXSZV76NV2Y7YIK6CDHSY4ZTCR653LDJP65WI72XFFRFWARKBY7YAC5FEA",
			"type": "pay"
		}
	}
}
```
