import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from utils import apply_style, page_header, disclaimer, LOGO

apply_style()
st.set_page_config(page_title="RugRadar — Watchlist", page_icon="📋", layout="wide")
page_header("Watchlist", "Ajoute tes tokens et suis-les en temps réel")

# ── Plan check ──
if "user_plan" not in st.session_state:
    st.session_state["user_plan"] = "free"
plan = st.session_state["user_plan"]
tier = {"free": 0, "pro": 1, "ultimate": 2}
FREE_LIMIT = 4

plan_labels = {"free": "🆓 Gratuit", "pro": "⚡ Pro", "ultimate": "💎 Ultimate"}
st.caption(f"Plan : {plan_labels.get(plan, 'Gratuit')}")

# ── Session state ──
if "custom_watchlist" not in st.session_state:
    st.session_state["custom_watchlist"] = [
        ("solana", "So11111111111111111111111111111111111111112", "SOL"),
        ("solana", "EKpQGSJtjMFqHFYzQ2RzBLH2K3cNoHGKutQYd2LQfC5X", "WIF"),
        ("solana", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "BONK"),
        ("solana", "JUPyiwrYJFskkApdCuW5Ys5CKiSRJDQ2p1BoBBU13wF", "JUP"),
    ]

# ── Add token ──
st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
st.markdown("<div class='rr-card-title'>➕ Ajouter un token</div>", unsafe_allow_html=True)

current_count = len(st.session_state["custom_watchlist"])
if plan == "free" and current_count >= FREE_LIMIT:
    st.warning(f"🔒 Limite gratuite atteinte ({FREE_LIMIT} tokens max).")
    if st.button("⚡ Passer Pro", type="primary"):
        st.switch_page("pages/prenium_page.py")
else:
    with st.form("add_token_form"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            new_chain = st.selectbox("Chain", ["solana", "ethereum", "bsc", "base", "arbitrum"], index=0)
        with col_b:
            new_addr = st.text_input("Adresse du token", placeholder="0x... ou adresse Solana")
        with col_c:
            new_label = st.text_input("Label (optionnel)", placeholder="Nom du token")
        submitted = st.form_submit_button("Ajouter", type="primary")

    if submitted and new_addr:
        existing = [addr for _, addr, _ in st.session_state["custom_watchlist"]]
        if new_addr in existing:
            st.warning("Déjà dans la watchlist.")
        else:
            label = new_label.strip() if new_label.strip() else new_addr[:8] + "..."
            st.session_state["custom_watchlist"].append((new_chain, new_addr, label))
            st.success(f"Ajouté : {label}")
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ── Remove token ──
wl = st.session_state["custom_watchlist"]
if wl:
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>🗑️ Retirer un token</div>", unsafe_allow_html=True)
    to_remove = st.selectbox("Choisir", options=range(len(wl)),
                             format_func=lambda i: f"{wl[i][2]} ({wl[i][0]}) — {wl[i][1][:12]}...")
    if st.button("Retirer", type="secondary"):
        wl.pop(to_remove)
        st.session_state["custom_watchlist"] = wl
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Fetch live data ──
@st.cache_data(ttl=60)
def fetch_token_data(chain, addr):
    try:
        r = requests.get(f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{addr}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("pairs"): return data["pairs"][0]
    except Exception:
        pass
    return None

rows, errors = [], []
for chain, addr, label in wl:
    pair = fetch_token_data(chain, addr)
    if pair:
        base = pair.get("baseToken", {})
        rows.append({
            "Ticker": base.get("symbol", label),
            "Nom": base.get("name", label),
            "Prix": float(pair.get("priceUsd", 0) or 0),
            "24h": pair.get("priceChange", {}).get("h24", 0) or 0,
            "MCap": pair.get("marketCap", 0) or 0,
            "Liq": pair.get("liquidity", {}).get("usd", 0) or 0,
            "Vol": pair.get("volume", {}).get("h24", 0) or 0,
        })
    else:
        errors.append(label)

if errors:
    st.warning(f"Indisponible : {', '.join(errors)}")

if rows:
    df = pd.DataFrame(rows)

    st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
    for label, val in [("Tokens", len(df)), ("Hausse", (df["24h"] > 0).sum()),
                       ("Baisse", (df["24h"] < 0).sum()),
                       ("Volume", f"${df['Vol'].sum()/1e3:.0f}K" if df['Vol'].sum() < 1e6 else f"${df['Vol'].sum()/1e6:.1f}M")]:
        st.markdown(f"""<div class='metric-pill'><div class='val'>{val}</div><div class='lbl'>{label}</div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📊 Données en direct</div>", unsafe_allow_html=True)

    sortby = st.selectbox("Trier par", ["MCap", "24h", "Vol", "Prix"])
    view = df.sort_values(sortby, ascending=False)

    st.dataframe(view, use_container_width=True, hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Nom": st.column_config.TextColumn("Nom", width="medium"),
            "Prix": st.column_config.NumberColumn("Prix", format="$%.6f"),
            "24h": st.column_config.NumberColumn("24h", format="%.1f%%"),
            "MCap": st.column_config.NumberColumn("MCap", format="$%.0f"),
            "Liq": st.column_config.NumberColumn("Liq", format="$%.0f"),
            "Vol": st.column_config.NumberColumn("Vol 24h", format="$%.0f"),
        })

    fig = go.Figure()
    colors = ["#22c55e" if x >= 0 else "#f85149" for x in view["24h"]]
    fig.add_trace(go.Bar(x=view["Ticker"], y=view["24h"], marker_color=colors))
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10),
                      showlegend=False, yaxis_title="24h %",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.02)",
                      font={"color": "white"}, yaxis={"gridcolor": "rgba(255,255,255,.06)"})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Aucun token dans la watchlist.")

disclaimer()
