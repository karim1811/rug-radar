import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

LOGO = "https://user-gen-media-assets.s3.amazonaws.com/gemini_images/2877ac40-2405-4447-b8a8-4526ddbadd72.png"

st.set_page_config(page_title="RugRadar — Dashboard", page_icon="🔍", layout="wide")
st.markdown("""
<style>
.stApp { background: #0b1020; }
section[data-testid="stSidebar"] { background: #09101b; }
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("RugRadar")
st.caption("Dashboard temps reel — Fear & Greed, Trending, Top Coins")

# ── APIs ──
@st.cache_data(ttl=120)
def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/", params={"limit": 7}, timeout=10)
        if r.status_code == 200:
            return r.json().get("data", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=120)
def get_trending():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
        if r.status_code == 200:
            return r.json().get("coins", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=120)
def get_top_market():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 20,
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h",
            },
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

# ── Fetch all ──
with st.spinner("Chargement des donnees..."):
    fg_data = get_fear_greed()
    trending = get_trending()
    top_market = get_top_market()

# ── Top metrics ──
if top_market:
    btc = next((x for x in top_market if x.get("symbol") == "btc"), {})
    eth = next((x for x in top_market if x.get("symbol") == "eth"), {})
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("BTC", f"${btc.get('current_price', 0):,.0f}", f"{btc.get('price_change_percentage_24h', 0):.1f}%")
    m2.metric("ETH", f"${eth.get('current_price', 0):,.0f}", f"{eth.get('price_change_percentage_24h', 0):.1f}%")
    if fg_data:
        m3.metric("Fear & Greed", f"{fg_data[0].get('value', 'N/A')}/100", fg_data[0].get("value_classification", ""))
    else:
        m3.metric("Fear & Greed", "N/A")
    m4.metric("Trending", str(len(trending)))

st.write("")

# ── Row: Fear & Greed gauge + Trending table ──
col_left, col_right = st.columns([1, 1.5], gap="large")

with col_left:
    st.subheader("Fear & Greed Index")
    if fg_data:
        val = int(fg_data[0].get("value", 50))
        cls = fg_data[0].get("value_classification", "Neutral")
        color = "#ef4444" if val <= 25 else "#f59e0b" if val <= 50 else "#84cc16" if val <= 75 else "#22c55e"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={"font": {"color": "white", "size": 32}},
            title={"text": cls, "font": {"color": "#8b949e", "size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "white"},
                "bar": {"color": color},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 1,
                "bordercolor": "rgba(255,255,255,0.15)",
                "steps": [
                    {"range": [0, 25], "color": "#b91c1c"},
                    {"range": [25, 50], "color": "#f59e0b"},
                    {"range": [50, 75], "color": "#84cc16"},
                    {"range": [75, 100], "color": "#22c55e"},
                ],
            },
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "white"}, height=260, margin=dict(l=10, r=10, t=30, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        # 7-day history
        if len(fg_data) > 1:
            dates = [x.get("timestamp", "")[:10] for x in reversed(fg_data)]
            vals = [int(x.get("value", 0)) for x in reversed(fg_data)]
            fig2 = go.Figure(go.Scatter(x=dates, y=vals, mode="lines+markers",
                line={"color": "#8b5cf6", "width": 3}, marker={"size": 6},
                fill="tozeroy", fillcolor="rgba(139,92,246,0.1)"))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)",
                font={"color": "white"}, height=200, margin=dict(l=10, r=10, t=10, b=10),
                xaxis={"gridcolor": "rgba(255,255,255,0.08)"},
                yaxis={"gridcolor": "rgba(255,255,255,0.08)", "range": [0, 100]},
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("API Fear & Greed indisponible")

with col_right:
    st.subheader("🔥 Trending CoinGecko")
    if trending:
        rows = []
        for c in trending[:10]:
            item = c.get("item", {})
            rows.append({
                "Nom": item.get("name", ""),
                "Ticker": item.get("symbol", "").upper(),
                "Rank": item.get("market_cap_rank", "N/A"),
                "Score": item.get("score", 0),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
            column_config={
                "Nom": st.column_config.TextColumn("Nom", width="medium"),
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Rank": st.column_config.TextColumn("Rank", width="small"),
                "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=10, format="%d"),
            })
    else:
        st.info("API CoinGecko indisponible")

st.write("")

# ── Top market table ──
if top_market:
    st.subheader("📊 Top marche")
    rows = []
    for x in top_market:
        rows.append({
            "#": x.get("market_cap_rank", 0),
            "Ticker": x.get("symbol", "").upper(),
            "Nom": x.get("name", ""),
            "Prix": x.get("current_price", 0) or 0,
            "24h": x.get("price_change_percentage_24h", 0) or 0,
            "MarketCap": x.get("market_cap", 0) or 0,
            "Volume": x.get("total_volume", 0) or 0,
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True,
        column_config={
            "#": st.column_config.TextColumn("#", width="small"),
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Nom": st.column_config.TextColumn("Nom", width="medium"),
            "Prix": st.column_config.NumberColumn("Prix", format="$%.4f"),
            "24h": st.column_config.NumberColumn("24h", format="%.1f%%"),
            "MarketCap": st.column_config.NumberColumn("Market Cap", format="$%.0f"),
            "Volume": st.column_config.NumberColumn("Volume 24h", format="$%.0f"),
        })

st.write("")

# ── Quick nav ──
st.subheader("Acces rapide")
b1, b2, b3, b4 = st.columns(4)
if b1.button("🔍 RugRadar", use_container_width=True):
    st.switch_page("pages/rugradar_page.py")
if b2.button("📋 Watchlist", use_container_width=True):
    st.switch_page("pages/watchlist_page.py")
if b3.button("📈 Tokens", use_container_width=True):
    st.switch_page("pages/token_pages.py")
if b4.button("🚨 Signaux", use_container_width=True):
    st.switch_page("pages/signals_pages.py")
