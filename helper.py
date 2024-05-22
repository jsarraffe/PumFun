import base64
import requests


def get_quote(quote_type, mint, amount, slippage):
    ############################################
    # Gets a "buy" or "sell" quote for a token #
    #                                          #
    # Parameters:                              #
    # - quote_type (str): "buy" or "sell"      #
    # - mint (str): Token mint address         #
    # - amount (int): Amount in lamports       #
    #   (1 SOL = 1e9 lamports)                 #
    # - slippage (int): Desired slippage       #
    #                                          #
    # Returns:                                 #
    # - dict: Quote data if successful         #
    # - None: If the request fails             #
    ############################################  
    
    ##### EXAMPLE USAGE #######
    # quote_type = "sell"  # "buy" or "sell"
    # mint = "5NejGhNyARVgGSZ8jiqiBdqkiZbYHxTjMN9sMqLmuBKS"  # Token mint address
    # amount = 100000  # Amount in lamports (0.0001 SOL)
    # slippage = 5  # Desired slippage
    # quote = get_quote(quote_type, mint, amount, slippage)
 
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
 
    return response
def get_balance(wallet_address, mint_address):
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

    ############################################
    # Buys a specified amount of a token       #
    #                                          #
    # Parameters:                              #
    # - input_mint (str): SOL mint address     #
    # - output_mint (str): Token mint address  #
    # - amount_in_sol (float): Amount of SOL to use for buying #
    # - wallet_address (str): Wallet address   #
    # - private_key (str): Wallet private key  #
    # - slippage (int): Desired slippage       #
    # - priority_fee (float): Priority fee in SOL #
    #                                          #
    # Returns:                                 #
    # - dict: Buy transaction data if successful #
    # - None: If the request fails             #
    ############################################

    # Convert SOL to lamports (1 SOL = 1e9 lamports)
    amount_in_lamports = int(amount_in_sol * 1e9)

    # Get buy quote
    quote = get_quote("buy", input_mint, output_mint, amount_in_lamports, slippage)
    if quote is None or quote.get("outAmount", 0) <= 0:
        print("Failed to get a valid quote.")
        return None

    # Execute buy
    url_trade = "https://pumpapi.fun/api/trade"
    payload_trade = {
        "trade_type": "buy",
        "mint": output_mint,
        "amount": amount_in_lamports,
        "slippage": slippage,
        "priorityFee": priority_fee,
        "userPrivateKey": private_key
    }
    response_trade = requests.post(url_trade, json=payload_trade)
    if response_trade.status_code == 200:
        trade_data = response_trade.json()
        print(f"Buy Transaction ID: {trade_data['tx_hash']}")
        return trade_data
    else:
        print(f"Error executing buy trade: {response_trade.status_code} - {response_trade.text}")
        return None
def perform_buy_trade(mint, amount_in_sol, slippage, priority_fee, wallet_address):
    ############################################
    # Performs a buy trade for a specified amount#
    #                                          #
    # Parameters:                              #
    # - mint (str): Token mint address         #
    # - amount_in_sol (float): Amount in SOL to use for buying #
    # - slippage (int): Desired slippage       #
    # - priority_fee (float): Priority fee in SOL #
    # - wallet_address (str): Your public key  #
    #                                          #
    # Returns:                                 #
    # - dict: Transaction data if successful   #
    # - None: If the request fails             #
    ############################################



    # Example usage
    # mint = "5NejGhNyARVgGSZ8jiqiBdqkiZbYHxTjMN9sMqLmuBKS"  # Token mint address
    # amount_in_sol = 0.01  # Example amount in SOL
    # slippage = 5  # Desired slippage
    # priority_fee = 0.003  # Priority fee in SOL
    # wallet_address = "2RcEamY9tuMLbQep28BqTK2kpByy95iT6bdXqgNHUADC"  # Your public key

    # perform_buy_trade(mint, amount_in_sol, slippage, priority_fee, wallet_address)

    url = "https://pumpapi.fun/api/trade_transaction"
    payload = {
        "trade_type": "buy",
        "mint": mint,
        "amount": amount_in_sol,
        "slippage": slippage,
        "priorityFee": priority_fee,
        "userPublicKey": wallet_address
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        transaction = response.json()["transaction"]
        print(f"Transaction: {transaction}")
        return transaction
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
def perform_sell_trade(wallet_address, mint_address, percentage, slippage, private_key):
    # Get the token balance
    balance_in_tokens = get_balance(wallet_address, mint_address)
    if balance_in_tokens is None:
        print("Failed to retrieve balance.")
        return None
    
    # Calculate the amount to sell based on the percentage
    amount_to_sell = balance_in_tokens * (percentage / 100)
    print(f"Amount to sell in tokens: {amount_to_sell}")
    
    # Get a quote for selling the amount
    quote = get_quote("sell", mint_address, amount_to_sell, slippage)
    if quote is None:
        print("Failed to get a valid sell quote.")
        return None
    
    # Execute the sell trade
    url_trade = "https://pumpapi.fun/api/trade"
    payload_trade = {
        "trade_type": "sell",
        "mint": mint_address,
        "amount": amount_to_sell,
        "slippage": slippage,
        "priorityFee": 0.003,  # Example priority fee in SOL
        "userPrivateKey": private_key
    }
    
    response_trade = requests.post(url_trade, json=payload_trade)
    if response_trade.status_code == 200:
        trade_data = response_trade.json()
        print(f"Sell Transaction ID: {trade_data['tx_hash']}")
        return trade_data
    else:
        print(f"Error executing sell trade: {response_trade.status_code} - {response_trade.text}")
        return None
