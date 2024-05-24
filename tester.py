import requests

url = "https://pumpapi.fun/api/trade"
payload = {
    "trade_type": "buy",                    # Buy or sell 
    "mint": "DpbbGCQSxTrQc6jPAbSHzptnnr2FbowwJGWE3aevTbev",            # Token mint address
    "amount": 0.01,                         # Amount in SOL , if buying or of tokens if selling.
    "slippage": 5,                          # Desired slippage 
    "priorityFee": 0.003,                   # Value in SOL
    "userPrivateKey": "3CuaoY1Bb2NKipfSGenpvTWeXWd9iC1UvxtNrce5JU6x3LYF6kyYLm82jkpf55v9tchB8Ukk2cGeTmSnxygEK6vY"   # Wallet private key 
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    transaction_id = response.json()["tx_hash"]
    print(f"Transaction ID: {transaction_id}")
else:
    print(f"Error: {response.status_code} - {response.text}")
