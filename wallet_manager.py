import os
import base58
import requests
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams
from dotenv import load_dotenv
import asyncio

class WalletManager:
    def __init__(self, env_file='wallet_keys.env'):
        load_dotenv(env_file)
        self.keys = {
            'HEAD_HUNCHO_PRIVATE_KEY': os.getenv('HEAD_HUNCHO_PRIVATE_KEY'),
            'PRIVATE_KEY2': os.getenv('PRIVATE_KEY2'),
            'PRIVATE_KEY3': os.getenv('PRIVATE_KEY3'),
            'PRIVATE_KEY4': os.getenv('PRIVATE_KEY4'),
            'PRIVATE_KEY5': os.getenv('PRIVATE_KEY5'),
            'PRIVATE_KEY6': os.getenv('PRIVATE_KEY6'),
            'PRIVATE_KEY7': os.getenv('PRIVATE_KEY7'),
            'PRIVATE_KEY8': os.getenv('PRIVATE_KEY8'),
        }
        self.public_keys = {name: self.get_public_key_from_private(pk) for name, pk in self.keys.items()}
        self.client = Client("https://api.mainnet-beta.solana.com")

    def get_public_key_from_private(self, private_key_str):
        private_key_bytes = base58.b58decode(private_key_str)
        keypair = Keypair.from_secret_key(private_key_bytes)
        return keypair.public_key

    def get_sol_balance(self, public_key):
        response = self.client.get_balance(public_key)
        if response['result']:
            sol_balance = response['result']['value'] / 1e9  # Convert lamports to SOL
            print(f"SOL Balance for {public_key}: {sol_balance} SOL")
            return sol_balance
        else:
            print(f"Error retrieving balance for {public_key}")
            return None

    def get_all_sol_balances(self):
        return {name: self.get_sol_balance(pk) for name, pk in self.public_keys.items()}

    def get_token_balance(self, wallet_address, mint_address):
        url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet_address,
                {"mint": mint_address},
                {"encoding": "jsonParsed"}
            ]
        }

        response = requests.post(url, json=payload, headers=headers)   
        if response.status_code == 200:
            try:
                result = response.json()["result"]["value"]
                if result:
                    token_balance = result[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
                    print(f"Token Balance: {token_balance} tokens")
                    return token_balance
                else:
                    print("No token accounts found for the given mint address.")
                    return None
            except (IndexError, KeyError) as e:
                print(f"Error extracting token balance: {e}")
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def transfer_sol(self, from_private_key, to_public_key, amount_sol):
        from_keypair = Keypair.from_secret_key(base58.b58decode(from_private_key))
        to_pubkey = PublicKey(to_public_key)
        amount_lamports = int(amount_sol * 1e9)  # Convert SOL to lamports

        transaction = Transaction()
        transaction.add(
            transfer(
                TransferParams(
                    from_pubkey=from_keypair.public_key,
                    to_pubkey=to_pubkey,
                    lamports=amount_lamports
                )
            )
        )

        response = self.client.send_transaction(transaction, from_keypair)
        if response.get('result'):
            print(f"Transaction successful: {response['result']}")
            return response['result']
        else:
            print(f"Transaction failed: {response}")
            return None

    async def top_up_bot_wallets(self, amount_sol):
        head_huncho_private_key = self.keys['HEAD_HUNCHO_PRIVATE_KEY']
        for name, public_key in self.public_keys.items():
            if name != 'HEAD_HUNCHO_PRIVATE_KEY':
                result = self.transfer_sol(head_huncho_private_key, public_key, amount_sol)
                if result:
                    print(f"Top up {name} ({public_key}): Successful, Transaction ID: {result}")
                else:
                    print(f"Top up {name} ({public_key}): Failed")
                await asyncio.sleep(2)  # Adding delay to handle rate limits

    def print_public_keys(self):
        for name, public_key in self.public_keys.items():
            print(f"{name}: {public_key}")

# Sample usage
if __name__ == "__main__":
    wallet_manager = WalletManager()

    # Print public keys
    wallet_manager.print_public_keys()

    # Top up all bot wallets with 0.001 SOL
    asyncio.run(wallet_manager.top_up_bot_wallets(0.001))
