import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

LOGO = "https://user-gen-media-assets.s3.amazonaws.com/gemini_images/2877ac40-2405-4447-b8a8-4526ddbadd72.png"

st.set_page_config(page_title="Watchlist", page_icon=LOGO, layout="wide")
st.markdown("""
<style>
.stApp { background: #0b1020; }
.header-wrap{display:flex;align-items:center;gap:12px;margin-bottom:1rem;}
.header-img{width:48px;height:48px;border-radius:14px;object-fit:cover;box-shadow:0 4px 14px rgba(0,0,0,.25);}
.header-title{font-size:2rem;font-weight:800;line-height:1;color:#fff;}
</style>
""", unsafe_allow_html=True)
st.markdown(f"<div class='header-wrap'><img class='header-img' src='{LOGO}'><div class='header-title'>RugRadar</div></div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 8])
with col1:
    if st.button("Menu", use_container_width=True):
        st.switch_page("main.py")
with col2:
    st.title("Watchlist")
    st.caption("Suivi des tokens en temps reel via DexScreener + CoinGecko.")

# ── Default watchlist tokens (Solana) ──
DEFAULT_TOKENS = [
    ("solana", "So11111111111111111111111111111111111111112", "SOL"),
    ("solana", "EKpQGSJtjMFqHFYzQ2RzBLH2K3cNoHGKutQYd2LQfC5X", "WIF"),
    ("solana", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "BONK"),
    ("solana", "JUPyiwrYJFskkApdCuW5Ys5CKiSRJDQ2p1BoBBU13wF", "JUP"),
]

@st.cache_data(ttl=60)
def fetch_watchlist():
    rows = []
    for chain, addr, fallback in DEFAULT_TOKENS:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{addr}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("pairs"):
                    p = data["pairs"][0]
                    base = p.get("baseToken", {})
                    liq = p.get("liquidity", {}).get("usd", 0) or 0
                    vol = p.get("volume", {}).get("h24", 0) or 0
                    mcap = p.get("marketCap", 0) or 0
                    pc = p.get("priceChange", {})
                    price = float(p.get("priceUsd", 0) or 0)
                    rows.append({
                        "Ticker": base.get("symbol", fallback),
                        "Nom": base.get("name", fallback),
                        "Prix": price,
                        "24h": pc.get("h24", 0) or 0,
                        "MarketCap": mcap,
                        "Liquidity": liq,
                        "Volume24h": vol,
                    })
        except Exception:
            pass
    return pd.DataFrame(rows)

with st.spinner("Chargement des donnees live..."):
    df = fetch_watchlist()

if df.empty:
    st.warning("Impossible de recuperer les donnees. Verifie ta connexion.")
else:
    up = (df["24h"] > 0).sum()
    down = (df["24h"] < 0).sum()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tokens suivis", len(df))
    m2.metric("En hausse", up)
    m3.metric("En baisse", down)
    m4.metric("Volume total 24h", f"${df['Volume24h'].sum()/1e6:.1f}M" if df['Volume24h'].sum() > 1e6 else f"${df['Volume24h'].sum()/1e3:.0f}K")

    sortby = st.selectbox("Trier par", ["MarketCap", "24h", "Volume24h", "Prix"])
    view = df.sort_values(sortby, ascending=False)

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Nom": st.column_config.TextColumn("Nom", width="medium"),
            "Prix": st.column_config.NumberColumn("Prix", format="$%.6f"),
            "24h": st.column_config.NumberColumn("24h", format="%.1f%%"),
            "MarketCap": st.column_config.NumberColumn("Market Cap", format="$%.0f"),
            "Liquidity": st.column_config.NumberColumn("Liquidity", format="$%.0f"),
            "Volume24h": st.column_config.NumberColumn("Volume 24h", format="$%.0f"),
        },
    )
