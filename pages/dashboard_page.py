import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="RugRadar — Dashboard", page_icon="🔍", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #07111f 0%, #0c1628 50%, #111c2f 100%);
        color: white;
    }
    section[data-testid="stSidebar"] {
        background: #09101b;
    }
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("RugRadar")
st.caption("Dashboard inspiré des pages marché modernes")

m1, m2, m3, m4 = st.columns(4)
m1.metric("SOL", "$187.76", "+3.6%")
m2.metric("Tokens suivis", "126", "+12")
m3.metric("Signaux du jour", "7", "+2")
m4.metric("Fear & Greed", "28/100", "Fear")

top_left, top_right = st.columns([0.75, 1.25], gap="large")

with top_left:
    st.subheader("Fear & Greed")
    gauge_value = 28

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=gauge_value,
            number={"font": {"color": "white", "size": 28}},
            title={"text": "", "font": {"color": "white"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "white"},
                "bar": {"color": "#f43f5e"},
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
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        height=220,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Spécifications", expanded=False):
        st.write("**Valeur**: 28 / 100")
        st.write("**Lecture**: Fear modéré")
        st.write("**Message**: marché prudent, attention aux faux breakouts.")
        st.write("**Usage**: utile pour filtrer le contexte général.")

with top_right:
    st.subheader("Tendance du marché")
    chart = go.Figure()
    chart.add_trace(
        go.Scatter(
            x=["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
            y=[42, 45, 43, 49, 54, 58, 64],
            mode="lines+markers",
            line=dict(color="#8b5cf6", width=4),
            marker=dict(size=8, color="#c084fc"),
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.15)",
        )
    )
    chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font={"color": "white"},
        height=260,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", range=[0, 100]),
    )
    st.plotly_chart(chart, use_container_width=True)

st.markdown("## Vue portefeuille / marché")

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("Portefeuille Solana")
    wallet_rows = pd.DataFrame(
        [
            ["SOL", "4.25", "$797.40"],
            ["USDC", "512.00", "$512.00"],
            ["JUP", "140.00", "$137.20"],
        ],
        columns=["Asset", "Balance", "USD"],
    )
    st.dataframe(wallet_rows, use_container_width=True, hide_index=True)

with right:
    st.subheader("Trending CoinGecko-like")
    trending = pd.DataFrame(
        [
            ["Pudgy Penguins", "+5.5%", "Trending"],
            ["Zcash", "+16.3%", "Trending"],
            ["Hyperliquid", "+4.2%", "Trending"],
            ["Solana", "+3.6%", "Stable momentum"],
        ],
        columns=["Coin", "24h", "Tag"],
    )
    st.dataframe(trending, use_container_width=True, hide_index=True)

st.markdown("## Cryptos en vue")

df = pd.DataFrame(
    [
        ["SOL", "Solana", "$187.76", "+3.6%", "120.9B", "Momentum"],
        ["JUP", "Jupiter", "$0.98", "+11.2%", "1.4B", "Très fort"],
        ["BONK", "Bonk", "$0.000024", "-2.1%", "1.9B", "Faible"],
        ["PYTH", "Pyth", "$0.45", "+4.8%", "2.7B", "Fort"],
        ["WIF", "dogwifhat", "$2.31", "+7.9%", "2.3B", "Fort"],
    ],
    columns=["Ticker", "Nom", "Prix", "24h", "Market Cap", "Signal"],
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
        "Nom": st.column_config.TextColumn("Nom", width="medium"),
        "Prix": st.column_config.TextColumn("Prix", width="small"),
        "24h": st.column_config.TextColumn("24h", width="small"),
        "Market Cap": st.column_config.TextColumn("Market Cap", width="medium"),
        "Signal": st.column_config.TextColumn("Signal", width="small"),
    },
)

for ticker, name, price, chg, cap, signal in df.values:
    with st.expander(f"{ticker} — {name} | {price} | {chg}", expanded=False):
        st.write(f"**Market cap**: {cap}")
        st.write(f"**Signal**: {signal}")
        st.write("**Prévision simple**: surveiller le volume et la confirmation de tendance.")
        st.write("**Risque**: volatilité élevée, attention aux mouvements brusques.")

st.markdown("## Accès rapide")
b1, b2, b3, b4 = st.columns(4)
if b1.button("🔍 RugRadar"):
    st.switch_page("pages/rugradar_page.py")
if b2.button("Ouvrir les jetons"):
    st.switch_page("pages/token_pages.py")
if b3.button("Ouvrir les signaux"):
    st.switch_page("pages/signals_pages.py")
if b4.button("Ouvrir la watchlist"):
    st.switch_page("pages/watchlist_page.py")