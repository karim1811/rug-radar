import requests
import pandas as pd

HELlUS_API_KEY = "fbed4ec7-e264-44ea-8b2d-54f205837863"

def get_top_holders(mint, api_key):
    url = f"https://mainnet.helius-rpc.com/?api-key={api_key}"
    payload = {
        "jsonrpc": "2.0",
        "id": "my-id",
        "method": "getTokenLargestAccounts",
        "params": [mint]
    }
    response = requests.post(url, json=payload, timeout=30)
    print("STATUS:", response.status_code)
    print("RAW:", response.text)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise Exception(f"RPC error: {data['error']}")
    if "result" not in data:
        raise Exception(f"Unexpected response: {data}")
    return data["result"]["value"]

def main():
    mint = input("Entre le mint Solana du token : ").strip()
    holders = get_top_holders(mint, HELlUS_API_KEY)
    df = pd.DataFrame(holders)
    print(df.to_string(index=False))
    df.to_csv("output/top_holders.csv", index=False)
    print("CSV sauvegarde: output/top_holders.csv")

if __name__ == "__main__":
    main()
