import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

LOGO = "https://user-gen-media-assets.s3.amazonaws.com/gemini_images/2877ac40-2405-4447-b8a8-4526ddbadd72.png"

st.set_page_config(page_title="Signaux", page_icon=LOGO, layout="wide")
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
    st.title("Signaux")
    st.caption("Signaux achat/vente generes automatiquement depuis les donnees live.")

# ── Fetch trending from CoinGecko ──
@st.cache_data(ttl=120)
def fetch_trending():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
        if r.status_code == 200:
            return r.json().get("coins", [])
    except Exception:
        pass
    return []

# ── Fetch pair from DexScreener by query ──
@st.cache_data(ttl=60)
def fetch_dex_pair(query: str, chain: str = "solana"):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={query} {chain}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pairs = r.json().get("pairs", [])
            if pairs:
                return pairs[0]
    except Exception:
        pass
    return None

# ── Risk scoring (same logic as rugradar) ──
def calc_risk(pair: dict) -> tuple:
    score = 50
    if not pair:
        return score, "N/A", "#8b949e"
    mcap = pair.get("marketCap", 0) or 0
    liq = pair.get("liquidity", {}).get("usd", 0) or 0
    vol = pair.get("volume", {}).get("h24", 0) or 0
    pc = pair.get("priceChange", {})
    chg24 = pc.get("h24", 0) or 0
    created = pair.get("pairCreatedAt", 0) or 0

    if mcap < 100_000: score += 15
    elif mcap < 500_000: score += 10
    elif mcap > 100_000_000: score -= 10
    elif mcap > 10_000_000: score -= 5

    if liq < 10_000: score += 20
    elif liq < 50_000: score += 15
    elif liq < 200_000: score += 5
    elif liq > 1_000_000: score -= 10

    if liq > 0:
        ratio = vol / liq
        if ratio > 10: score += 20
        elif ratio > 5: score += 15
        elif ratio > 2: score += 8

    if chg24 > 500: score += 15
    elif chg24 > 200: score += 10
    elif chg24 > 100: score += 5
    elif chg24 < -90: score += 15
    elif chg24 < -70: score += 10

    if created > 0:
        age_d = (time.time() * 1000 - created) / (1000 * 86400)
        if age_d < 1: score += 15
        elif age_d < 7: score += 10
        elif age_d < 30: score += 5
        elif age_d > 365: score -= 10

    score = max(0, min(100, score))
    if score <= 30:
        return score, "LOW", "#3fb950"
    elif score <= 60:
        return score, "MEDIUM", "#d29922"
    return score, "HIGH", "#f85149"

# ── Build signals ──
@st.cache_data(ttl=120)
def build_signals():
    trending = fetch_trending()
    rows = []
    for coin in trending[:10]:
        name = coin.get("item", {}).get("name", "")
        symbol = coin.get("item", {}).get("symbol", "")
        pair = fetch_dex_pair(name)
        if pair:
            score, risk_lvl, color = calc_risk(pair)
            mcap = pair.get("marketCap", 0) or 0
            chg = (pair.get("priceChange", {}).get("h24", 0) or 0)
            if score <= 40 and chg > 0:
                action = "ACHAT"
            elif score >= 70 or chg < -20:
                action = "VENTE"
            else:
                action = "ATTENTE"
            rows.append({
                "Ticker": symbol,
                "Nom": name,
                "Action": action,
                "Score": score,
                "Risque": risk_lvl,
                "24h": chg,
                "MarketCap": mcap,
            })
    return pd.DataFrame(rows)

with st.spinner("Analyse des tokens trending en cours..."):
    df = build_signals()

if df.empty:
    st.warning("Pas de signaux disponibles. API peut etre rate-limite.")
else:
    buys = (df["Action"] == "ACHAT").sum()
    sells = (df["Action"] == "VENTE").sum()
    waits = (df["Action"] == "ATTENTE").sum()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Signaux ACHAT", buys)
    m2.metric("Signaux VENTE", sells)
    m3.metric("En attente", waits)
    m4.metric("Score moyen", f'{df["Score"].mean():.0f}')

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        action_filter = st.selectbox("Filtrer", ["Tous", "ACHAT", "VENTE", "ATTENTE"])
    with col_f2:
        risk_filter = st.selectbox("Risque", ["Tous", "LOW", "MEDIUM", "HIGH"])

    view = df.copy()
    if action_filter != "Tous":
        view = view[view["Action"] == action_filter]
    if risk_filter != "Tous":
        view = view[view["Risque"] == risk_filter]
    view = view.sort_values("Score", ascending=True)

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Nom": st.column_config.TextColumn("Nom", width="medium"),
            "Action": st.column_config.TextColumn("Action", width="small"),
            "Score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100),
            "Risque": st.column_config.TextColumn("Risque", width="small"),
            "24h": st.column_config.NumberColumn("24h", format="%.1f%%"),
            "MarketCap": st.column_config.NumberColumn("Market Cap", format="$%.0f"),
        },
    )

    # Bar chart
    st.subheader("📊 Repartition des signaux")
    fig = go.Figure()
    for action, color in [("ACHAT", "#22c55e"), ("ATTENTE", "#d29922"), ("VENTE", "#ef4444")]:
        sub = df[df["Action"] == action]
        if not sub.empty:
            fig.add_trace(go.Bar(x=sub["Ticker"], y=sub["Score"], name=action, marker_color=color))
    fig.update_layout(
        barmode="group",
        height=350,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font={"color": "white"},
        yaxis=dict(title="Risk Score", gridcolor="rgba(255,255,255,0.08)"),
    )
    st.plotly_chart(fig, use_container_width=True)
