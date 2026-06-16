import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from utils import apply_style, page_header, disclaimer, LOGO

apply_style()
st.set_page_config(page_title="RugRadar — Dashboard", page_icon="📊", layout="wide")
page_header("Dashboard", "Vue d'ensemble du marché crypto")

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

@st.cache_data(ttl=60)
def get_top_market():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 20,
                    "page": 1, "sparkline": "true", "price_change_percentage": "24h,7d"},
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=120)
def get_global_data():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=10)
        if r.status_code == 200:
            return r.json().get("data", {})
    except Exception:
        pass
    return {}

with st.spinner("Chargement..."):
    fg_data = get_fear_greed()
    trending = get_trending()
    top_market = get_top_market()
    global_data = get_global_data()

# ── Global metrics ──
if global_data:
    st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
    mc = global_data.get("total_market_cap", {}).get("usd", 0)
    vol = global_data.get("total_volume", {}).get("usd", 0)
    btc_dom = global_data.get("market_cap_percentage", {}).get("btc", 0)
    eth_dom = global_data.get("market_cap_percentage", {}).get("eth", 0)
    coins = global_data.get("active_cryptocurrencies", 0)
    markets = global_data.get("markets", 0)

    metrics = [
        ("Cap. marché totale", f"${mc/1e12:.2f}T"),
        ("Volume 24h", f"${vol/1e9:.1f}B"),
        ("BTC Dominance", f"{btc_dom:.1f}%"),
        ("ETH Dominance", f"{eth_dom:.1f}%"),
        ("Cryptos actives", f"{coins:,}"),
        ("Markets", f"{markets:,}"),
    ]
    for label, val in metrics:
        st.markdown(f"""<div class='metric-pill'><div class='val'>{val}</div><div class='lbl'>{label}</div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")

# ── Row 1: Fear & Greed + Trending ──
col_fg, col_trend = st.columns([1, 1.2], gap="large")

with col_fg:
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>😱 Fear & Greed Index</div>", unsafe_allow_html=True)
    if fg_data:
        val = int(fg_data[0].get("value", 50))
        cls = fg_data[0].get("value_classification", "Neutral")
        color = "#ef4444" if val <= 25 else "#f59e0b" if val <= 50 else "#84cc16" if val <= 75 else "#22c55e"
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            number={"font": {"color": "white", "size": 36}},
            title={"text": cls, "font": {"color": "#484f58", "size": 13}},
            gauge={"axis": {"range": [0, 100], "tickcolor": "white"}, "bar": {"color": color},
                   "bgcolor": "rgba(0,0,0,0)", "borderwidth": 1, "bordercolor": "rgba(255,255,255,.12)",
                   "steps": [
                       {"range": [0, 25], "color": "rgba(239,68,68,.15)"},
                       {"range": [25, 50], "color": "rgba(245,158,11,.15)"},
                       {"range": [50, 75], "color": "rgba(132,204,22,.15)"},
                       {"range": [75, 100], "color": "rgba(34,197,94,.15)"},
                   ]},
        ))
        fig.update_layout(height=240, margin=dict(l=10, r=10, t=35, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"})
        st.plotly_chart(fig, use_container_width=True)

        if len(fg_data) > 1:
            dates = [x.get("timestamp", "")[:10] for x in reversed(fg_data)]
            vals = [int(x.get("value", 0)) for x in reversed(fg_data)]
            fig2 = go.Figure(go.Scatter(
                x=dates, y=vals, mode="lines+markers",
                line={"color": "#8b5cf6", "width": 2}, marker={"size": 5},
                fill="tozeroy", fillcolor="rgba(139,92,246,.08)"
            ))
            fig2.update_layout(height=160, margin=dict(l=10, r=10, t=5, b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.02)",
                               font={"color": "white"}, xaxis={"gridcolor": "rgba(255,255,255,.05)"},
                               yaxis={"gridcolor": "rgba(255,255,255,.05)", "range": [0, 100]})
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("API indisponible")
    st.markdown("</div>", unsafe_allow_html=True)

with col_trend:
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>🔥 Trending CoinGecko</div>", unsafe_allow_html=True)
    if trending:
        rows = []
        for i, c in enumerate(trending[:10]):
            item = c.get("item", {})
            rows.append({"#": i+1, "Nom": item.get("name", ""), "Ticker": item.get("symbol", "").upper(),
                         "Rank": item.get("market_cap_rank", "N/A"), "Score": item.get("score", 0)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=380,
            column_config={"#": st.column_config.TextColumn("#", width="small"),
                           "Nom": st.column_config.TextColumn("Nom", width="medium"),
                           "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                           "Rank": st.column_config.TextColumn("Rank", width="small"),
                           "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=10)})
    else:
        st.info("API indisponible")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Row 2: Market chart + Top movers ──
if top_market:
    st.write("")
    col_chart, col_movers = st.columns([1.5, 1], gap="large")

    with col_chart:
        st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
        st.markdown("<div class='rr-card-title'>📊 Top 20 — Variation 24h</div>", unsafe_allow_html=True)

        df = pd.DataFrame([{
            "Ticker": x.get("symbol", "").upper(),
            "Nom": x.get("name", ""),
            "Prix": x.get("current_price", 0) or 0,
            "24h": x.get("price_change_percentage_24h", 0) or 0,
            "7d": x.get("price_change_percentage_7d_in_currency", 0) or 0,
            "MCap": x.get("market_cap", 0) or 0,
            "Volume": x.get("total_volume", 0) or 0,
            "Spark": x.get("sparkline_in_7d", {}).get("price", []),
        } for x in top_market])

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
        st.markdown("</div>", unsafe_allow_html=True)

    with col_movers:
        st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
        st.markdown("<div class='rr-card-title'>🚀 Top Movers 24h</div>", unsafe_allow_html=True)

        sorted_df = df.sort_values("24h", ascending=False)
        top_5 = sorted_df.head(5)
        bottom_5 = sorted_df.tail(5).sort_values("24h")

        st.markdown("**🟢 Plus fortes hausses :**")
        for _, row in top_5.iterrows():
            st.markdown(f"<div style='display:flex;justify-content:space-between;padding:3px 0;'>"
                        f"<span><strong>{row['Ticker']}</strong> <span style='color:#484f58;font-size:.8rem;'>{row['Nom'][:12]}</span></span>"
                        f"<span style='color:#3fb950;font-weight:700;'>{row['24h']:+.1f}%</span></div>", unsafe_allow_html=True)

        st.write("")
        st.markdown("**🔴 Plus fortes baisses :**")
        for _, row in bottom_5.iterrows():
            st.markdown(f"<div style='display:flex;justify-content:space-between;padding:3px 0;'>"
                        f"<span><strong>{row['Ticker']}</strong> <span style='color:#484f58;font-size:.8rem;'>{row['Nom'][:12]}</span></span>"
                        f"<span style='color:#f85149;font-weight:700;'>{row['24h']:+.1f}%</span></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Sparkline comparison chart ──
    st.write("")
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📈 Comparaison Top 10 (7 jours, normalisé)</div>", unsafe_allow_html=True)
    fig3 = go.Figure()
    for _, row in df.head(10).iterrows():
        prices = row.get("Spark", [])
        if prices and prices[0] != 0:
            normalized = [(p / prices[0] - 1) * 100 for p in prices]
            fig3.add_trace(go.Scatter(y=normalized, mode="lines", name=row["Ticker"], line=dict(width=1.5)))
    fig3.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.02)",
                       font={"color": "white"}, showlegend=True,
                       legend={"font": {"color": "#8b949e", "size": 10}, "orientation": "h", "y": -0.15},
                       xaxis={"visible": False}, yaxis={"gridcolor": "rgba(255,255,255,.06)", "title": "%"})
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Full table ──
if top_market:
    st.write("")
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📋 Tableau complet</div>", unsafe_allow_html=True)
    st.dataframe(df[["Ticker", "Nom", "Prix", "24h", "7d", "MCap", "Volume", "Spark"]],
                 use_container_width=True, hide_index=True, height=400,
                 column_config={
                     "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                     "Nom": st.column_config.TextColumn("Nom", width="medium"),
                     "Prix": st.column_config.NumberColumn("Prix", format="$%.4f"),
                     "24h": st.column_config.NumberColumn("24h", format="%.1f%%"),
                     "7d": st.column_config.NumberColumn("7d", format="%.1f%%"),
                     "MCap": st.column_config.NumberColumn("MCap", format="$%.0f"),
                     "Volume": st.column_config.NumberColumn("Volume", format="$%.0f"),
                     "Spark": st.column_config.LineChartColumn("7J", width="small"),
                 })
    st.markdown("</div>", unsafe_allow_html=True)

disclaimer()
