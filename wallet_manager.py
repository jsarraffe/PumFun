import os
import base58
import requests
import time
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from spl.token.instructions import transfer_checked, TransferCheckedParams
from dotenv import load_dotenv
import asyncio

def get_associated_token_address(wallet_address, token_mint_address):
    """Get the associated token address for a wallet and mint."""
    return PublicKey.find_program_address(
        [bytes(wallet_address), bytes(TOKEN_PROGRAM_ID), bytes(token_mint_address)],
        ASSOCIATED_TOKEN_PROGRAM_ID,
    )[0]

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

    def get_mint_decimals(self, mint_address):
        mint_pubkey = PublicKey(mint_address)
        mint_info = self.client.get_token_supply(mint_pubkey)
        if 'result' in mint_info:
            return mint_info['result']['value']['decimals']
        else:
            raise Exception(f"Failed to get mint decimals for {mint_address}")

    def transfer_tokens(self, from_private_key, to_public_key, mint_address, amount):
        from_keypair = Keypair.from_secret_key(base58.b58decode(from_private_key))
        from_pubkey = from_keypair.public_key
        to_pubkey = PublicKey(to_public_key)
        mint_pubkey = PublicKey(mint_address)
        
        # Get associated token accounts
        from_token_account = get_associated_token_address(from_pubkey, mint_pubkey)
        to_token_account = get_associated_token_address(to_pubkey, mint_pubkey)
        
        # Get the mint decimals
        mint_decimals = self.get_mint_decimals(mint_address)

        transaction = Transaction()
        transaction.add(
            transfer_checked(
                TransferCheckedParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=from_token_account,
                    mint=mint_pubkey,
                    dest=to_token_account,
                    owner=from_pubkey,
                    amount=amount,
                    decimals=mint_decimals
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

    def transfer_all_tokens_back_to_head_huncho(self, mint_address):
        head_huncho_private_key = self.keys['HEAD_HUNCHO_PRIVATE_KEY']
        head_huncho_public_key = self.get_public_key_from_private(head_huncho_private_key)
        for name, private_key_str in self.keys.items():
            if name != 'HEAD_HUNCHO_PRIVATE_KEY':
                public_key = self.get_public_key_from_private(private_key_str)
                balance_in_tokens = self.get_token_balance(str(public_key), mint_address)
                if balance_in_tokens and balance_in_tokens > 0:
                    mint_decimals = self.get_mint_decimals(mint_address)
                    balance_in_atomic_units = int(balance_in_tokens * (10 ** mint_decimals))
                    print(f"Transferring {balance_in_atomic_units} atomic units from {public_key} to Head Huncho ({head_huncho_public_key})")
                    transfer_result = self.transfer_tokens(private_key_str, head_huncho_public_key, mint_address, balance_in_atomic_units)
                    if transfer_result:
                        print(f"Transfer from {name} ({public_key}) to Head Huncho: Successful, Transaction ID: {transfer_result}")
                    else:
                        print(f"Error executing token transfer from {name} ({public_key})")
                # Add a delay to avoid rate limiting
                time.sleep(5)

    def print_public_keys(self):
        for name, public_key in self.public_keys.items():
            print(f"{name}: {public_key}")

# Sample usage
if __name__ == "__main__":
    wallet_manager = WalletManager()

    mint_address = "DpbbGCQSxTrQc6jPAbSHzptnnr2FbowwJGWE3aevTbev"  # Replace with your mint address
    wallet_manager.transfer_all_tokens_back_to_head_huncho(mint_address)
