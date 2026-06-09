import requests
import streamlit as st

BASE_URL = "https://api.coingecko.com/api/v3"


@st.cache_data(ttl=60)
def get_top_coins(vs_currency="usd", per_page=50, page=1):
    url = f"{BASE_URL}/coins/markets"
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
    return r.json()


@st.cache_data(ttl=300)
def search_coin(query):
    url = f"{BASE_URL}/search"
    params = {"query": query}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("coins", [])


@st.cache_data(ttl=300)
def get_coin_details(coin_id, vs_currency="usd"):
    url = f"{BASE_URL}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false",
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    market = data.get("market_data", {})

    return {
        "id": data.get("id"),
        "symbol": data.get("symbol"),
        "name": data.get("name"),
        "image": data.get("image", {}).get("large"),
        "current_price": market.get("current_price", {}).get(vs_currency),
        "market_cap": market.get("market_cap", {}).get(vs_currency),
        "total_volume": market.get("total_volume", {}).get(vs_currency),
        "high_24h": market.get("high_24h", {}).get(vs_currency),
        "low_24h": market.get("low_24h", {}).get(vs_currency),
        "price_change_24h": market.get("price_change_percentage_24h"),
        "price_change_7d": market.get("price_change_percentage_7d"),
        "price_change_30d": market.get("price_change_percentage_30d"),
        "homepage": data.get("links", {}).get("homepage", [None])[0],
        "explorer": (data.get("links", {}).get("blockchain_site", [None]) or [None])[0],
        "categories": data.get("categories", []),
    }