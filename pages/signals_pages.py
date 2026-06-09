import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
st.markdown(f"<div class='header-wrap'><img class='header-img' src='{LOGO}'><div class='header-title'>Aladin Crypto</div></div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 8])
with col1:
    if st.button("Menu", use_container_width=True):
        st.switch_page("main.py")
with col2:
    st.title("Signaux")
    st.caption("Lecture rapide des opportunités et des risques.")

@st.cache_data(ttl=300)
def data():
    return pd.DataFrame([
        ["SOL", "Solana", "Achat", 92, 3.6, "Breakout confirmé", "Très fort", "Solana ecosystem"],
        ["JUP", "Jupiter", "Achat", 88, 11.2, "Momentum fort", "Fort", "DeFi"],
        ["BONK", "Bonk", "Attente", 61, -2.1, "Rotation possible", "Neutre", "Memecoin"],
        ["PYTH", "Pyth", "Achat", 79, 4.8, "Reprise propre", "Fort", "Oracle"],
        ["WIF", "dogwifhat", "Achat", 84, 7.9, "Volume en hausse", "Fort", "Memecoin"],
        ["JTO", "Jito", "Attente", 57, -1.3, "Consolidation", "Neutre", "Solana ecosystem"],
        ["RAY", "Raydium", "Achat", 73, 2.4, "Rebond technique", "Fort", "DeFi"],
        ["DRIFT", "Drift", "Vente", 42, -4.6, "Sous pression", "Faible", "Perps"],
        ["TNSR", "Tensor", "Achat", 68, 5.1, "Rebond spéculatif", "Neutre", "NFT"],
        ["MOBILE", "Helium Mobile", "Vente", 31, -6.2, "Faiblesse persistante", "Faible", "Infra"],
    ], columns=["Ticker", "Nom", "Action", "Score", "24h", "Lecture", "Force", "Catégorie"])

df = data()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Signaux achat", int((df["Action"] == "Achat").sum()))
m2.metric("Signaux vente", int((df["Action"] == "Vente").sum()))
m3.metric("Score moyen", f'{df["Score"].mean():.0f}')
m4.metric("Signaux forts", int(df["Force"].isin(["Fort", "Très fort"]).sum()))

scoremin = st.slider("Score minimum", 0, 100, 60, 1)
category = st.selectbox("Catégorie", ["Toutes"] + sorted(df["Catégorie"].unique().tolist()))
view = df[df["Score"] >= scoremin].copy()
if category != "Toutes":
    view = view[view["Catégorie"] == category]
view = view.sort_values("Score", ascending=False)

st.dataframe(
    view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker", pinned=True, width="small"),
        "Nom": st.column_config.TextColumn("Nom", width="medium"),
        "Action": st.column_config.TextColumn("Action", width="small"),
        "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
        "24h": st.column_config.NumberColumn("24h", format="%.1f"),
        "Lecture": st.column_config.TextColumn("Lecture", width="large"),
        "Force": st.column_config.TextColumn("Force", width="medium"),
        "Catégorie": st.column_config.TextColumn("Catégorie", width="medium"),
    }
)

radar = df.groupby("Catégorie", as_index=False)["Score"].mean()
fig = go.Figure()
fig.add_trace(go.Bar(x=radar["Catégorie"], y=radar["Score"], marker_color=["#22c55e" if x >= 70 else "#f59e0b" if x >= 50 else "#ef4444" for x in radar["Score"]]))
fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(range=[0, 100]))
st.plotly_chart(fig, use_container_width=True)