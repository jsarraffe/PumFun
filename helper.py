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
            "quote_type": quote_type,  # "buy" or "sell"
            "mint": mint,              # Token mint address
            "amount": amount,          # Amount in lamports (1 SOL = 1e9 lamports)
            "slippage": slippage       # Desired slippage
        }
        response = requests.post(url=url_quote, json=payload_quote)   
        if response.status_code == 200:
            quote_data = response.json()
            print(f"Quote: {quote_data}")
            return quote_data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None 

    def perform_buy_trade(self, mint, amount_in_sol, slippage, priority_fee, wallet_address):
        amount_in_lamports = int(amount_in_sol * 1e9)
        quote = self.get_quote("buy", mint, amount_in_lamports, slippage)
        if quote is None or quote.get("outAmount", 0) <= 0:
            print("Failed to get a valid quote.")
            return None

        url_trade = "https://pumpapi.fun/api/trade"
        payload_trade = {
            "trade_type": "buy",
            "mint": mint,
            "amount": amount_in_lamports,
            "slippage": slippage,
            "priorityFee": priority_fee,
            "userPrivateKey": self.keys['HEAD_HUNCHO_PRIVATE_KEY']
        }
        response_trade = requests.post(url_trade, json=payload_trade)
        if response_trade.status_code == 200:
            trade_data = response_trade.json()
            print(f"Buy Transaction ID: {trade_data['tx_hash']}")
            return trade_data
        else:
            print(f"Error executing buy trade: {response_trade.status_code} - {response_trade.text}")
            return None

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
            "priorityFee": 0.003,  # Example priority fee in SOL
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

    def transfer_tokens_back_to_head_huncho(self, wallet_address, mint_address):
        balance_in_tokens = self.get_token_balance(wallet_address, mint_address)
        if balance_in_tokens is None or balance_in_tokens == 0:
            print("No tokens to transfer.")
            return None
        
        url_transfer = "https://pumpapi.fun/api/transfer"
        payload_transfer = {
            "from": wallet_address,
            "to": self.public_keys['HEAD_HUNCHO_PRIVATE_KEY'],
            "amount": balance_in_tokens,
            "mint": mint_address,
            "userPrivateKey": self.keys[wallet_address]
        }
        
        response_transfer = requests.post(url_transfer, json=payload_transfer)
        if response_transfer.status_code == 200:
            transfer_data = response_transfer.json()
            print(f"Transfer Transaction ID: {transfer_data['tx_hash']}")
            return transfer_data
        else:
            print(f"Error executing token transfer: {response_transfer.status_code} - {response_transfer.text}")
            return None

# Sample usage
if __name__ == "__main__":
    wallet_manager = WalletManager()

    # Print public keys
    wallet_manager.print_public_keys()

    # Top up all bot wallets with 0.001 SOL
    #asyncio.run(wallet_manager.top_up_bot_wallets(0.001))

    # Perform buy trade for 0.01 SOL of DpbbGCQSxTrQc6jPAbSHzptnnr2FbowwJGWE3aevTbev
    mint_address = "DpbbGCQSxTrQc6jPAbSHzptnnr2FbowwJGWE3aevTbev"
    amount_in_sol = 0.01
    slippage = 0.01  # Example slippage
    priority_fee = 0.003  # Example priority fee

    for key_name in ['PRIVATE_KEY2', 'PRIVATE_KEY3', 'PRIVATE_KEY4', 'PRIVATE_KEY5', 'PRIVATE_KEY6', 'PRIVATE_KEY7', 'PRIVATE_KEY8']:
        print(f"Buying with {key_name}...")
        trade_result = wallet_manager.perform_buy_trade(mint_address, amount_in_sol, slippage, priority_fee, key_name)
        if trade_result:
            print(f"Trade successful for {key_name}: {trade_result}")
        else:
            print(f"Trade failed for {key_name}")
