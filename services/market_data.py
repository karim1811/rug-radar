import requests
import pandas as pd

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def get_top_coins(vs_currency="usd", per_page=6, page=1):
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False,
        "price_change_percentage": "24h",
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    rows = []
    for x in data:
        rows.append({
            "Ticker": x.get("symbol", "").upper(),
            "Nom": x.get("name", ""),
            "Prix": x.get("current_price", 0),
            "24h": x.get("price_change_percentage_24h", 0),
            "MarketCap": x.get("market_cap", 0),
            "Volume": x.get("total_volume", 0),
        })
    return pd.DataFrame(rows)