import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time
from utils import apply_style, page_header, disclaimer, plan_gate, LOGO

apply_style()
st.set_page_config(page_title="RugRadar — Signaux", page_icon="🚨", layout="wide")
page_header("Signaux de trading", "ACHAT / VENTE / ATTENTE — Basé sur l'analyse de risque")

plan_gate("pro")

# ── APIs ──
@st.cache_data(ttl=120)
def fetch_trending():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
        if r.status_code == 200:
            return r.json().get("coins", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=60)
def fetch_dex_pair(query: str, chain: str = "solana"):
    try:
        r = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={query} {chain}", timeout=10)
        if r.status_code == 200:
            pairs = r.json().get("pairs", [])
            if pairs: return pairs[0]
    except Exception:
        pass
    return None

def calc_risk(pair: dict) -> tuple:
    score = 50
    if not pair: return score, "N/A", "#8b949e"
    mcap = pair.get("marketCap", 0) or 0
    liq = pair.get("liquidity", {}).get("usd", 0) or 0
    vol = pair.get("volume", {}).get("h24", 0) or 0
    chg24 = pair.get("priceChange", {}).get("h24", 0) or 0
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
    if score <= 30: return score, "LOW", "#3fb950"
    elif score <= 60: return score, "MEDIUM", "#d29922"
    return score, "HIGH", "#f85149"

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
            chg = pair.get("priceChange", {}).get("h24", 0) or 0
            if score <= 40 and chg > 0: action = "ACHAT"
            elif score >= 70 or chg < -20: action = "VENTE"
            else: action = "ATTENTE"
            rows.append({"Ticker": symbol, "Nom": name, "Action": action,
                         "Score": score, "Risque": risk_lvl, "24h": chg, "MarketCap": mcap})
    return pd.DataFrame(rows)

with st.spinner("Analyse des tokens trending..."):
    df = build_signals()

if df.empty:
    st.warning("Pas de signaux disponibles. API peut être rate-limitée.")
else:
    # ── Summary metrics ──
    buys = (df["Action"] == "ACHAT").sum()
    sells = (df["Action"] == "VENTE").sum()
    waits = (df["Action"] == "ATTENTE").sum()

    st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
    for label, val, color in [("🟢 ACHAT", buys, "#3fb950"), ("🔴 VENTE", sells, "#f85149"), ("🟡 ATTENTE", waits, "#d29922")]:
        st.markdown(f"""<div class='metric-pill'><div class='val' style='color:{color};'>{val}</div><div class='lbl'>{label}</div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class='metric-pill'><div class='val'>{df['Score'].mean():.0f}</div><div class='lbl'>Score moyen</div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ── Signal cards ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📡 Signaux en temps réel</div>", unsafe_allow_html=True)

    for _, row in df.iterrows():
        action = row["Action"]
        badge_cls = "badge-buy" if action == "ACHAT" else "badge-sell" if action == "VENTE" else "badge-wait"
        risk_cls = "badge-risk-low" if row["Risque"] == "LOW" else "badge-risk-med" if row["Risque"] == "MEDIUM" else "badge-risk-high"
        border_color = "rgba(63,185,80,.2)" if action == "ACHAT" else "rgba(248,81,73,.2)" if action == "VENTE" else "rgba(210,153,34,.2)"

        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:10px;
                    border:1px solid {border_color};margin:6px 0;background:rgba(255,255,255,.02);'>
          <div style='flex:1;'>
            <strong style='font-size:1.05rem;'>{row['Nom']}</strong>
            <span style='color:#484f58;font-size:.85rem;margin-left:6px;'>{row['Ticker']}</span>
          </div>
          <div style='text-align:right;min-width:70px;'>
            <div style='color:{"#3fb950" if row["24h"] >= 0 else "#f85149"};font-weight:700;'>{row["24h"]:+.1f}%</div>
            <div style='font-size:.72rem;color:#484f58;'>24h</div>
          </div>
          <span class='{risk_cls}'>{row["Risque"]} {row["Score"]}</span>
          <span class='{badge_cls}'>{action}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ── Chart ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📊 Répartition des signaux</div>", unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig = go.Figure()
        for action, color in [("ACHAT", "#22c55e"), ("ATTENTE", "#d29922"), ("VENTE", "#ef4444")]:
            sub = df[df["Action"] == action]
            if not sub.empty:
                fig.add_trace(go.Bar(x=sub["Ticker"], y=sub["Score"], name=action, marker_color=color))
        fig.update_layout(barmode="group", height=300, margin=dict(l=10, r=10, t=10, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.02)",
                          font={"color": "white"}, legend={"font": {"color": "#8b949e"}},
                          yaxis={"title": "Risk Score", "gridcolor": "rgba(255,255,255,.06)"})
        st.plotly_chart(fig, use_container_width=True)

    with col_c2:
        # Pie chart
        counts = df["Action"].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=counts.index, values=counts.values,
            marker_colors=["#22c55e" if l == "ACHAT" else "#d29922" if l == "ATTENTE" else "#ef4444" for l in counts.index],
            hole=0.5, textinfo="label+percent", textfont={"color": "white", "size": 12}
        ))
        fig2.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10),
                           paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"},
                           showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Table ──
    st.write("")
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📋 Tableau détaillé</div>", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        action_filter = st.selectbox("Filtrer par action", ["Tous", "ACHAT", "VENTE", "ATTENTE"])
    with col_f2:
        risk_filter = st.selectbox("Filtrer par risque", ["Tous", "LOW", "MEDIUM", "HIGH"])

    view = df.copy()
    if action_filter != "Tous": view = view[view["Action"] == action_filter]
    if risk_filter != "Tous": view = view[view["Risque"] == risk_filter]
    view = view.sort_values("Score", ascending=True)

    st.dataframe(view, use_container_width=True, hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Nom": st.column_config.TextColumn("Nom", width="medium"),
            "Action": st.column_config.TextColumn("Action", width="small"),
            "Score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100),
            "Risque": st.column_config.TextColumn("Risque", width="small"),
            "24h": st.column_config.NumberColumn("24h", format="%.1f%%"),
            "MarketCap": st.column_config.NumberColumn("MCap", format="$%.0f"),
        })
    st.markdown("</div>", unsafe_allow_html=True)

disclaimer()
