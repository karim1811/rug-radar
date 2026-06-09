import streamlit as st
import pandas as pd

from services.coingecko_service import get_top_coins, get_coin_details, search_coin

st.title("Dashboard crypto")

st.caption("Recherche de tokens et aperçu marché via CoinGecko.")

query = st.text_input("Rechercher un token", placeholder="BTC, ETH, Solana...")

if query:
    results = search_coin(query)
    options = {f"{c['name']} ({c['symbol'].upper()})": c["id"] for c in results[:10]}
else:
    options = {}

top = get_top_coins(per_page=25)

top_options = {
    f"#{coin['market_cap_rank']} {coin['name']} ({coin['symbol'].upper()})": coin["id"]
    for coin in top
    if coin.get("id")
}

all_options = {**options, **top_options}

selected_label = st.selectbox(
    "Choisir un actif",
    options=list(all_options.keys()) if all_options else ["BTC"],
)

selected_id = all_options.get(selected_label, "bitcoin")
coin = get_coin_details(selected_id)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Prix", f"${coin.get('current_price'):,.2f}" if coin.get("current_price") else "N/A")
col2.metric("Market cap", f"${coin.get('market_cap'):,.0f}" if coin.get("market_cap") else "N/A")
col3.metric("Volume 24h", f"${coin.get('total_volume'):,.0f}" if coin.get("total_volume") else "N/A")
col4.metric(
    "Variation 24h",
    f"{coin.get('price_change_24h'):.2f}%" if coin.get("price_change_24h") is not None else "N/A"
)

st.divider()

c1, c2 = st.columns([2, 1])

with c1:
    st.subheader(f"{coin.get('name')} ({coin.get('symbol', '').upper()})")
    st.write(f"ID CoinGecko : `{coin.get('id')}`")
    if coin.get("homepage"):
        st.link_button("Site officiel", coin["homepage"])
    if coin.get("explorer"):
        st.link_button("Explorer", coin["explorer"])

with c2:
    st.subheader("Vue rapide")
    st.write(f"High 24h : {coin.get('high_24h', 'N/A')}")
    st.write(f"Low 24h : {coin.get('low_24h', 'N/A')}")
    st.write(f"7d : {coin.get('price_change_7d', 'N/A')}")
    st.write(f"30d : {coin.get('price_change_30d', 'N/A')}")

st.divider()

st.subheader("Top coins")
table = pd.DataFrame(top)[
    ["market_cap_rank", "name", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"]
]
st.dataframe(table, use_container_width=True, hide_index=True)