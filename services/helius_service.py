import requests

WALLET_BASE_URL = "https://api.helius.xyz/v1/wallet"
RPC_URL = "https://mainnet.helius-rpc.com/?api-key={}"


def helius_get(url, api_key, params=None):
    headers = {"X-Api-Key": api_key}
    r = requests.get(url, headers=headers, params=params or {}, timeout=30)
    r.raise_for_status()
    return r.json()


def helius_post(api_key, method, params):
    url = RPC_URL.format(api_key)
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": method,
        "params": params,
    }
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise Exception(data["error"])
    return data.get("result", {})


def get_wallet_balances(wallet, api_key):
    return helius_get(f"{WALLET_BASE_URL}/{wallet}/balances", api_key)


def get_wallet_history(wallet, api_key):
    return helius_get(f"{WALLET_BASE_URL}/{wallet}/history", api_key, {"limit": 25})


def get_wallet_transfers(wallet, api_key):
    return helius_get(f"{WALLET_BASE_URL}/{wallet}/transfers", api_key, {"limit": 25})


def get_wallet_funded_by(wallet, api_key):
    return helius_get(f"{WALLET_BASE_URL}/{wallet}/funded-by", api_key)


def get_token_supply(mint_address, api_key):
    return helius_post(api_key, "getTokenSupply", [mint_address])


def get_token_largest_accounts(mint_address, api_key):
    return helius_post(api_key, "getTokenLargestAccounts", [mint_address])


def get_token_asset(mint_address, api_key):
    return helius_post(
        api_key,
        "getAsset",
        {
            "id": mint_address,
            "options": {"showFungible": True},
        },
    )