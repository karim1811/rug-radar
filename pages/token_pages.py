import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

LOGO = "https://user-gen-media-assets.s3.amazonaws.com/gemini_images/2877ac40-2405-4447-b8a8-4526ddbadd72.png"

st.set_page_config(page_title="Tokens", page_icon=LOGO, layout="wide")
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
    st.title("Tokens")
    st.caption("Top coins du marche — donnees CoinGecko en temps reel.")

@st.cache_data(ttl=120)
def fetch_top_coins(per_page=50):
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": per_page,
                "page": 1,
                "sparkline": "true",
                "price_change_percentage": "24h,7d",
            },
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            rows = []
            for x in data:
                rows.append({
                    "Rank": x.get("market_cap_rank", 0),
                    "Ticker": x.get("symbol", "").upper(),
                    "Nom": x.get("name", ""),
                    "Prix": x.get("current_price", 0) or 0,
                    "24h": x.get("price_change_percentage_24h", 0) or 0,
                    "7d": x.get("price_change_percentage_7d_in_currency", 0) or 0,
                    "MarketCap": x.get("market_cap", 0) or 0,
                    "Volume": x.get("total_volume", 0) or 0,
                    "Sparkline": x.get("sparkline_in_7d", {}).get("price", []),
                })
            return pd.DataFrame(rows)
    except Exception:
        pass
    return pd.DataFrame()

with st.spinner("Chargement du top coins via CoinGecko..."):
    df = fetch_top_coins()

if df.empty:
    st.warning("API CoinGecko indisponible. Reessaie dans un moment.")
else:
    up = (df["24h"] > 0).sum()
    down = (df["24h"] < 0).sum()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tokens", len(df))
    m2.metric("En hausse 24h", up)
    m3.metric("En baisse 24h", down)
    m4.metric("Dominance BTC", f"${df.iloc[0]['MarketCap']/df['MarketCap'].sum()*100:.0f}%" if len(df) > 0 else "N/A")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sortby = st.selectbox("Trier par", ["MarketCap", "24h", "7d", "Volume", "Prix"])
    with col_f2:
        top_n = st.slider("Afficher top", 5, 50, 20)

    view = df.sort_values(sortby, ascending=False).head(top_n)

    st.dataframe(
        view[["Rank", "Ticker", "Nom", "Prix", "24h", "7d", "MarketCap", "Volume", "Sparkline"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.TextColumn("#", width="small"),
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Nom": st.column_config.TextColumn("Nom", width="medium"),
            "Prix": st.column_config.NumberColumn("Prix", format="$%.4f"),
            "24h": st.column_config.NumberColumn("24h", format="%.1f%%"),
            "7d": st.column_config.NumberColumn("7d", format="%.1f%%"),
            "MarketCap": st.column_config.NumberColumn("Market Cap", format="$%.0f"),
            "Volume": st.column_config.NumberColumn("Volume 24h", format="$%.0f"),
            "Sparkline": st.column_config.LineChartColumn("7J", width="small"),
        },
    )

    # spaghetti chart
    st.subheader("📊 Comparaison top 10 (7J sparkline)")
    fig = go.Figure()
    for _, row in df.head(10).iterrows():
        prices = row.get("Sparkline", [])
        if prices:
            # Normalize to % change from first value
            base = prices[0] if prices[0] != 0 else 1
            normalized = [(p / base - 1) * 100 for p in prices]
            fig.add_trace(go.Scatter(y=normalized, mode="lines", name=row["Ticker"], line=dict(width=2)))
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font={"color": "white"},
        xaxis=dict(visible=False),
        yaxis=dict(title="% change", gridcolor="rgba(255,255,255,0.08)"),
    )
    st.plotly_chart(fig, use_container_width=True)
