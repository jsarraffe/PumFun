import os
import base58
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from spl.token.instructions import transfer_checked, TransferCheckedParams
from dotenv import load_dotenv
import requests

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

    def get_quote(self, quote_type, mint, amount, slippage):
        url_quote = "https://pumpapi.fun/api/quote"
        payload_quote = {
            "quote_type": quote_type,
            "mint": mint,
            "amount": amount,
            "slippage": slippage
        }
        response = requests.post(url_quote, json=payload_quote)
        if response.status_code == 200:
            quote_data = response.json()
            print(f"Quote: {quote_data}")
            return quote_data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def perform_buy_trade(self, mint, amount_in_sol, slippage, priority_fee, wallet_private_key):
        
     
        url = "https://pumpapi.fun/api/trade"
        payload = {
            "trade_type": "buy",                    # Buy or sell 
            "mint": fr"{mint}",            # Token mint address
            "amount": 0.01,                         # Amount in SOL , if buying or of tokens if selling.
            "slippage": 5,                          # Desired slippage 
            "priorityFee": 0.003,                   # Value in SOL
            "userPrivateKey": fr"{wallet_private_key}"   # Wallet private key 
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            transaction_id = response.json()["tx_hash"]
            print(f"Transaction ID: {transaction_id}")
            return True
        else:
            
            print(f"Error: {response.status_code} - {response.text}")
            return False



    def perform_sell_trade(self, wallet_address, mint_address, percentage, slippage):
        balance_in_tokens = self.get_token_balance(wallet_address, mint_address)
        if balance_in_tokens is None:
            print("Failed to retrieve balance.")
            return None

        amount_to_sell = balance_in_tokens * (percentage / 100)
        print(f"Amount to sell in tokens: {amount_to_sell}")

        quote = self.get_quote("sell", mint_address, amount_to_sell, slippage)
        if quote is None:
            print("Failed to get a valid sell quote.")
            return None

        url_trade = "https://pumpapi.fun/api/trade"
        payload_trade = {
            "trade_type": "sell",
            "mint": mint_address,
            "amount": amount_to_sell,
            "slippage": slippage,
            "priorityFee": 0.003,
            "userPrivateKey": self.keys[wallet_address]
        }

        response_trade = requests.post(url_trade, json=payload_trade)
        if response_trade.status_code == 200:
            trade_data = response_trade.json()
            print(f"Sell Transaction ID: {trade_data['tx_hash']}")
            return trade_data
        else:
            print(f"Error executing sell trade: {response_trade.status_code} - {response_trade.text}")
            return None

    def transfer_sol(self, from_private_key, to_public_key, amount_sol):
        from_keypair = Keypair.from_secret_key(base58.b58decode(from_private_key))
        to_pubkey = PublicKey(to_public_key)
        amount_lamports = int(amount_sol * 1e9)

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
                await asyncio.sleep(2)

    def print_public_keys(self):
        for name, public_key in self.public_keys.items():
            print(f"{name}: {public_key}")


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


# Sample usage
if __name__ == "__main__":
    wallet_manager = WalletManager()

    # Transfer tokens from PRIVATE_KEY2 to HEAD_HUNCHO_PRIVATE_KEY
    # from_key = wallet_manager.keys['PRIVATE_KEY2']
    # to_pubkey = wallet_manager.public_keys['HEAD_HUNCHO_PRIVATE_KEY']
    # mint_address = "DpbbGCQSxTrQc6jPAbSHzptnnr2FbowwJGWE3aevTbev"  # Replace with your mint address
    # amount = 1000  # Amount in the token's smallest unit

    # transfer_result = wallet_manager.transfer_tokens(from_key, to_pubkey, mint_address, amount)
    
    # if transfer_result:
    #     print(f"Transfer successful: {transfer_result}")
    # else:
    #     print("Transfer failed")


     #Perform buy trade for 0.01 SOL of DpbbGCQSxTrQc6jPAbSHzptnnr2FbowwJGWE3aevTbev
    mint_address = "DpbbGCQSxTrQc6jPAbSHzptnnr2FbowwJGWE3aevTbev"
    amount_in_sol = 0.01
    slippage = 5
    priority_fee = 0.003

    for key_name in ['PRIVATE_KEY2', 'PRIVATE_KEY3', 'PRIVATE_KEY4', 'PRIVATE_KEY5', 'PRIVATE_KEY6', 'PRIVATE_KEY7', 'PRIVATE_KEY8']:
        private_key = wallet_manager.keys[key_name]
        print(f"Buying with {key_name}...")
        trade_result = wallet_manager.perform_buy_trade(mint_address, amount_in_sol, slippage, priority_fee, private_key)
        if trade_result:
            print(f"Trade successful for {key_name}: {trade_result}")
        else:
            print(f"Trade failed for {key_name}")
