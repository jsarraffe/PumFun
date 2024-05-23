import requests

def get_quote():
    url_quote = "https://pumpapi.fun/api/quote"
    payload = {
        "quote_type": "buy",  # "buy" or "sell"
        "mint": "DpbbGCQSxTrQc6jPAbSHzptnnr2FbowwJGWE3aevTbev",  # Token mint address
        "amount": 100000,  # Amount in lamports (1 SOL = 1e9 lamports)
        "slippage": 5  # Desired slippage
    }
    
    try:
        response = requests.post(url_quote, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Quote Data:", data)
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

get_quote()
