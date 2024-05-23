import requests

# Fetch new wallets
url = "https://pumpapi.fun/api/generate_wallets"
params = {"n": 5}  # Number of wallets to generate

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    new_wallets = data.get('wallets', [])
    
    # Prepare the output string
    output = ""
    start_index = 4  # Start from PRIVATE_KEY4
    
    for i, wallet in enumerate(new_wallets, start=start_index):
        output += f"PRIVATE_KEY{i} = {wallet}\n"
    
    # Write the keys to the file
    with open("wallet_keys.env", "a") as f:
        f.write(output)

    print("Wallet private keys saved to wallet_keys.env")
else:
    print(f"Error retrieving data: {response.status_code}")
