import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from utils import apply_style, LOGO

apply_style()

st.set_page_config(page_title="RugRadar — Crypto Manipulation Detector", page_icon="🔍", layout="wide")

# ── Header ──
st.markdown(f"""
<div class="rr-header">
  <img class="rr-logo" src="{LOGO}">
  <div>
    <div class="rr-title">RugRadar</div>
    <div class="rr-sub">Crypto Manipulation Detector — Know When to Exit</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation ──
st.markdown("#### 📍 Navigation")
c1, c2, c3, c4, c5 = st.columns(5)
pages = [
    ("pages/rugradar_page.py", "🔍", "Scanner", "Rug pull detection"),
    ("pages/watchlist_page.py", "📋", "Watchlist", "Suivi personnalisé"),
    ("pages/token_pages.py", "📈", "Tokens", "Top marché"),
    ("pages/signals_pages.py", "🚨", "Signaux", "Signaux trading"),
    ("pages/dashboard.py", "📊", "Dashboard", "Vue d'ensemble"),
]
for col, (page, icon, label, desc) in zip([c1, c2, c3, c4, c5], pages):
    with col:
        st.page_link(page, label=f"{icon} {label}")
        st.caption(desc)

st.write("")

# ── Live data ──
@st.cache_data(ttl=60)
def get_home_market():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10,
                    "page": 1, "sparkline": "false", "price_change_percentage": "24h"},
            timeout=10,
        )
        if r.status_code == 200:
            return pd.DataFrame([{
                "Ticker": x.get("symbol", "").upper(),
                "Nom": x.get("name", ""),
                "Prix": x.get("current_price", 0) or 0,
                "24h": x.get("price_change_percentage_24h", 0) or 0,
                "MCap": x.get("market_cap", 0) or 0,
                "Volume": x.get("total_volume", 0) or 0,
            } for x in r.json()])
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=120)
def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/", params={"limit": 1}, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data: return data[0]
    except Exception:
        pass
    return None

@st.cache_data(ttl=120)
def get_trending():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
        if r.status_code == 200:
            return r.json().get("coins", [])[:5]
    except Exception:
        pass
    return []

df = get_home_market()
fg = get_fear_greed()
trending = get_trending()

# ── Hero stats ──
if not df.empty:
    btc = df[df["Ticker"] == "BTC"]
    eth = df[df["Ticker"] == "ETH"]
    btc_price = f"${btc.iloc[0]['Prix']:,.0f}" if not btc.empty else "N/A"
    btc_chg = f"{btc.iloc[0]['24h']:+.1f}%" if not btc.empty else ""
    eth_price = f"${eth.iloc[0]['Prix']:,.0f}" if not eth.empty else "N/A"
    eth_chg = f"{eth.iloc[0]['24h']:+.1f}%" if not eth.empty else ""
    fg_val = f"{fg.get('value', 'N/A')}/100" if fg else "N/A"
    fg_cls = fg.get("value_classification", "") if fg else ""
    fg_color = "#ef4444" if fg and int(fg.get("value", 50)) <= 25 else "#f59e0b" if fg and int(fg.get("value", 50)) <= 50 else "#22c55e"
    up_count = (df["24h"] > 0).sum()
    down_count = (df["24h"] < 0).sum()

    st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
    for label, val, color in [("BTC", f"{btc_price} {btc_chg}", "#f7931a"),
                                ("ETH", f"{eth_price} {eth_chg}", "#627eea"),
                                ("F&G", f"{fg_val} {fg_cls}", fg_color),
                                ("Hausse", str(up_count), "#22c55e"),
                                ("Baisse", str(down_count), "#f85149")]:
        st.markdown(f"""<div class='metric-pill'><div class='val' style='color:{color};'>{val}</div><div class='lbl'>{label}</div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ── Main content ──
left, right = st.columns([1.4, 1], gap="large")

with left:
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📊 Marché en direct — Top 10</div>", unsafe_allow_html=True)

    if df.empty:
        st.warning("API CoinGecko indisponible.")
    else:
        fig = go.Figure()
        colors = ["#22c55e" if x >= 0 else "#f85149" for x in df["24h"]]
        fig.add_trace(go.Bar(
            x=df["Ticker"], y=df["24h"], marker_color=colors,
            text=[f"{x:+.1f}%" for x in df["24h"]], textposition="outside",
            textfont={"color": "#c9d1d9", "size": 10},
        ))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10),
                          showlegend=False, yaxis_title="24h %",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.02)",
                          font={"color": "white"},
                          yaxis={"gridcolor": "rgba(255,255,255,.06)", "zerolinecolor": "rgba(255,255,255,.12)"})
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True, hide_index=True, height=360,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Nom": st.column_config.TextColumn("Nom", width="medium"),
                "Prix": st.column_config.NumberColumn("Prix", format="$%.4f"),
                "24h": st.column_config.NumberColumn("24h", format="%.1f%%"),
                "MCap": st.column_config.NumberColumn("MCap", format="$%.0f"),
                "Volume": st.column_config.NumberColumn("Volume", format="$%.0f"),
            })
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    # Fear & Greed
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>😱 Fear & Greed</div>", unsafe_allow_html=True)
    if fg:
        val = int(fg.get("value", 50))
        cls = fg.get("value_classification", "Neutral")
        color = "#ef4444" if val <= 25 else "#f59e0b" if val <= 50 else "#84cc16" if val <= 75 else "#22c55e"
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            number={"font": {"color": "white", "size": 32}},
            title={"text": cls, "font": {"color": "#484f58", "size": 12}},
            gauge={"axis": {"range": [0, 100], "tickcolor": "white"}, "bar": {"color": color},
                   "bgcolor": "rgba(0,0,0,0)", "borderwidth": 1, "bordercolor": "rgba(255,255,255,.1)",
                   "steps": [{"range": [0, 25], "color": "rgba(239,68,68,.12)"},
                             {"range": [25, 50], "color": "rgba(245,158,11,.12)"},
                             {"range": [50, 75], "color": "rgba(132,204,22,.12)"},
                             {"range": [75, 100], "color": "rgba(34,197,94,.12)"}]},
        ))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("API indisponible")
    st.markdown("</div>", unsafe_allow_html=True)

    # Trending
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>🔥 Trending</div>", unsafe_allow_html=True)
    if trending:
        for coin in trending:
            item = coin.get("item", {})
            st.markdown(f"**{item.get('name', '?')}** (`{item.get('symbol', '?').upper()}`) — Rank #{item.get('market_cap_rank', '-')}")
    else:
        st.info("Pas de trending")
    st.markdown("</div>", unsafe_allow_html=True)

    # Premium CTA
    st.markdown("<div class='rr-card' style='border-color:rgba(234,179,8,.2);background:linear-gradient(135deg,rgba(234,179,8,.06),rgba(10,14,26,.96));'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>⭐ Premium</div>", unsafe_allow_html=True)
    st.write("Signaux avancés, alertes Telegram, watchlist illimitée.")
    if st.button("👉 Voir les offres", use_container_width=True, type="primary"):
        st.switch_page("pages/prenium_page.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Disclaimer ──
st.markdown("""
<div class="rr-disclaimer">
⚠️ RugRadar est un outil d'analyse, PAS un conseil financier. Toujours DYOR. Crypto = risque de perte totale.
</div>
""", unsafe_allow_html=True)
