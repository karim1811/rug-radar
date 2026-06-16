import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from utils import apply_style, page_header, disclaimer, LOGO

apply_style()
st.set_page_config(page_title="RugRadar — Tokens", page_icon="📈", layout="wide")
page_header("Tokens", "Top 50 du marché — Données CoinGecko en temps réel")

@st.cache_data(ttl=120)
def fetch_top_coins(per_page=50):
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": per_page,
                    "page": 1, "sparkline": "true", "price_change_percentage": "24h,7d"},
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
                    "MCap": x.get("market_cap", 0) or 0,
                    "Volume": x.get("total_volume", 0) or 0,
                    "Spark": x.get("sparkline_in_7d", {}).get("price", []),
                })
            return pd.DataFrame(rows)
    except Exception:
        pass
    return pd.DataFrame()

with st.spinner("Chargement du top 50..."):
    df = fetch_top_coins()

if df.empty:
    st.warning("API CoinGecko indisponible.")
else:
    # ── Summary ──
    up = (df["24h"] > 0).sum()
    down = (df["24h"] < 0).sum()
    st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
    for label, val in [("Tokens", len(df)), ("Hausse 24h", up), ("Baisse 24h", down),
                       ("BTC Dom.", f"${df.iloc[0]['MCap']/df['MCap'].sum()*100:.0f}%")]:
        st.markdown(f"""<div class='metric-pill'><div class='val'>{val}</div><div class='lbl'>{label}</div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ── Top 10 cards ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>🏆 Top 10 en un coup d'œil</div>", unsafe_allow_html=True)

    cols = st.columns(5)
    for i, (_, row) in enumerate(df.head(10).iterrows()):
        col = cols[i % 5]
        color = "#3fb950" if row["24h"] >= 0 else "#f85149"
        with col:
            st.markdown(f"""
            <div style='text-align:center;padding:8px 4px;border-radius:10px;background:rgba(255,255,255,.03);margin-bottom:6px;'>
              <div style='font-size:.72rem;color:#484f58;'>#{row['Rank']} {row['Ticker']}</div>
              <div style='font-weight:800;font-size:.95rem;'>{row['Nom'][:14]}</div>
              <div style='font-weight:700;color:{color};'>{row['24h']:+.1f}%</div>
              <div style='font-size:.72rem;color:#484f58;'>${row['Prix']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ── Chart: Top 20 24h ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📊 Variations 24h — Top 20</div>", unsafe_allow_html=True)

    top20 = df.head(20)
    fig = go.Figure()
    colors = ["#22c55e" if x >= 0 else "#f85149" for x in top20["24h"]]
    fig.add_trace(go.Bar(
        x=top20["Ticker"], y=top20["24h"], marker_color=colors,
        text=[f"{x:+.1f}%" for x in top20["24h"]], textposition="outside",
        textfont={"color": "#c9d1d9", "size": 9},
    ))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                      showlegend=False, yaxis_title="24h %",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.02)",
                      font={"color": "white"},
                      yaxis={"gridcolor": "rgba(255,255,255,.06)", "zerolinecolor": "rgba(255,255,255,.12)"})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ── Sparkline comparison ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📈 Comparaison Top 10 (7 jours, normalisé)</div>", unsafe_allow_html=True)
    fig2 = go.Figure()
    for _, row in df.head(10).iterrows():
        prices = row.get("Spark", [])
        if prices and prices[0] != 0:
            normalized = [(p / prices[0] - 1) * 100 for p in prices]
            fig2.add_trace(go.Scatter(y=normalized, mode="lines", name=row["Ticker"], line=dict(width=1.5)))
    fig2.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.02)",
                       font={"color": "white"}, showlegend=True,
                       legend={"font": {"color": "#8b949e", "size": 10}, "orientation": "h", "y": -0.15},
                       xaxis={"visible": False}, yaxis={"gridcolor": "rgba(255,255,255,.06)", "title": "%"})
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ── Full table ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📋 Tableau complet</div>", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sortby = st.selectbox("Trier par", ["MCap", "24h", "7d", "Volume", "Prix"])
    with col_f2:
        top_n = st.slider("Afficher top", 5, 50, 20)

    view = df.sort_values(sortby, ascending=False).head(top_n)

    st.dataframe(view[["Rank", "Ticker", "Nom", "Prix", "24h", "7d", "MCap", "Volume", "Spark"]],
                 use_container_width=True, hide_index=True, height=400,
                 column_config={
                     "Rank": st.column_config.TextColumn("#", width="small"),
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
