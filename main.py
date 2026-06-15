import streamlit as st
import pandas as pd
import plotly.graph_objects as go

LOGO = "https://user-gen-media-assets.s3.amazonaws.com/gemini_images/2877ac40-2405-4447-b8a8-4526ddbadd72.png"

st.set_page_config(page_title="RugRadar — Crypto Manipulation Detector", page_icon="🔍", layout="wide")

st.markdown("""
<style>
.stApp { background: #0b1020; }
.header-wrap{display:flex;align-items:center;gap:14px;margin-bottom:1rem;padding:6px 0 10px 0;}
.header-img{width:54px;height:54px;border-radius:16px;object-fit:cover;box-shadow:0 4px 14px rgba(0,0,0,.28);flex-shrink:0;}
.header-title{font-size:2.15rem;font-weight:800;line-height:1.05;color:#fff;}
.card{padding:1rem 1.05rem;border-radius:18px;border:1px solid rgba(255,255,255,.08);background:linear-gradient(180deg, rgba(18,23,38,.96), rgba(10,14,24,.96));box-shadow:0 10px 32px rgba(0,0,0,.18);}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-wrap">
  <img class="header-img" src="{LOGO}">
  <div class="header-title">RugRadar</div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Accès rapide")
nav1, nav2, nav3, nav4 = st.columns(4)
with nav1:
    st.page_link("pages/rugradar_page.py", label="🔍 RugRadar")
with nav2:
    st.page_link("pages/watchlist_page.py", label="Liste de surveillance")
with nav3:
    st.page_link("pages/token_pages.py", label="Fiches jetons détaillées")
with nav4:
    st.page_link("pages/signals_pages.py", label="Signaux")

st.write("")

left, right = st.columns([1.3, 1])
with left:
    st.markdown("### Vue marché")
    df = pd.DataFrame({
        "Ticker": ["BTC", "ETH", "SOL", "BNB", "XRP"],
        "Nom": ["Bitcoin", "Ethereum", "Solana", "BNB", "XRP"],
        "24h": [1.8, 2.4, 3.6, 0.9, -1.2],
        "Signal": ["Fort", "Fort", "Momentum fort", "Neutre", "Faible"],
    })
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Ticker"], y=df["24h"], marker_color=["#22c55e" if x >= 0 else "#ef4444" for x in df["24h"]]))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, yaxis_title="24h %")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Premium")
    st.write("Le premium peut contenir des signaux avancés, des alertes privées et un suivi plus réactif.")
    st.link_button("Voir la page premium", "prenium_page.py")
    st.markdown("### Telegram")
    st.link_button("Ouvrir le bot Telegram", "https://t.me/ton_bot")
    st.markdown("</div>", unsafe_allow_html=True)