import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
    st.caption("Suivi des tokens et actifs à surveiller.")

@st.cache_data(ttl=300)
def data():
    return pd.DataFrame([
        ["SOL", "Solana", "L1", 187.76, 3.6, 120.9, "Momentum fort", [174, 176, 172, 178, 181, 185, 188]],
        ["JUP", "Jupiter", "DeFi", 0.98, 11.2, 1.4, "Breakout", [0.72, 0.75, 0.81, 0.88, 0.92, 0.95, 0.98]],
        ["BONK", "Bonk", "Memecoin", 0.000024, -2.1, 1.9, "Faible", [0.000026, 0.000025, 0.0000245, 0.0000248, 0.000024, 0.0000238, 0.000024]],
        ["PYTH", "Pyth", "Oracle", 0.45, 4.8, 2.7, "Fort", [0.39, 0.40, 0.41, 0.43, 0.44, 0.45, 0.45]],
        ["WIF", "dogwifhat", "Memecoin", 2.31, 7.9, 2.3, "Fort", [2.08, 2.05, 2.10, 2.18, 2.22, 2.27, 2.31]],
        ["JTO", "Jito", "Liquid Staking", 3.98, -1.3, 1.2, "Consolidation", [4.10, 4.05, 4.02, 4.00, 3.99, 3.97, 3.98]],
        ["RAY", "Raydium", "DeFi", 2.76, 2.4, 0.9, "Reprise", [2.62, 2.65, 2.67, 2.70, 2.73, 2.74, 2.76]],
        ["DRIFT", "Drift", "Perps", 1.89, -4.6, 0.7, "Sous pression", [2.02, 1.98, 1.95, 1.93, 1.91, 1.90, 1.89]],
    ], columns=["Ticker", "Nom", "Secteur", "Prix", "24h", "MarketCap", "Signal", "Trend"])

df = data()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Tokens suivis", len(df))
m2.metric("En hausse", int((df["24h"] > 0).sum()))
m3.metric("En baisse", int((df["24h"] < 0).sum()))
m4.metric("Signal fort", int(df["Signal"].isin(["Fort", "Momentum fort", "Breakout"]).sum()))

sector = st.selectbox("Secteur", ["Tous"] + sorted(df["Secteur"].unique().tolist()))
sortby = st.selectbox("Trier par", ["24h", "MarketCap", "Prix"])
order = st.selectbox("Ordre", ["Décroissant", "Croissant"])
view = df.copy()
if sector != "Tous":
    view = view[view["Secteur"] == sector]
view = view.sort_values(sortby, ascending=(order == "Croissant"))

st.dataframe(
    view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker", pinned=True, width="small"),
        "Nom": st.column_config.TextColumn("Nom", width="medium"),
        "Secteur": st.column_config.TextColumn("Secteur", width="medium"),
        "Prix": st.column_config.NumberColumn("Prix", format="%.6f"),
        "24h": st.column_config.NumberColumn("24h", format="%.1f"),
        "MarketCap": st.column_config.NumberColumn("Market Cap Bn", format="%.2f"),
        "Signal": st.column_config.TextColumn("Signal", width="medium"),
        "Trend": st.column_config.LineChartColumn("7J", y_min=min(min(x) for x in view["Trend"]), y_max=max(max(x) for x in view["Trend"])),
    }
)

for _, row in view.iterrows():
    with st.expander(f'{row["Ticker"]} - {row["Nom"]}', expanded=False):
        a, b, c = st.columns(3)
        a.metric("Prix", f'{row["Prix"]}')
        b.metric("24h", f'{row["24h"]}%')
        c.metric("Market cap", f'{row["MarketCap"]} Bn')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, 8)), y=row["Trend"], mode="lines+markers", line=dict(color="#22c55e", width=3), marker=dict(size=6), fill="tozeroy", fillcolor="rgba(34,197,94,0.12)"))
        fig.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)", xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig, use_container_width=True)