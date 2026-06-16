import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import time
from utils import apply_style, page_header, disclaimer, plan_gate, LOGO

apply_style()

# ── Page config ──
st.set_page_config(page_title="RugRadar — Scanner", page_icon="🔍", layout="wide")

page_header("RugRadar Scanner", "Analyse de risque crypto en temps réel — DexScreener")

# ── Search ──
st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
st.markdown("<div class='rr-card-title'>🔎 Rechercher un token</div>", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([3, 1])
with col_s1:
    search_query = st.text_input("Token", placeholder="Nom, symbole ou adresse de contrat (ex: WIF, SOL, 0x...)", label_visibility="collapsed")
with col_s2:
    chain = st.selectbox("Chain", ["solana", "ethereum", "bsc", "base", "arbitrum"], index=0, label_visibility="collapsed")

st.markdown("</div>", unsafe_allow_html=True)

# ── APIs ──
@st.cache_data(ttl=60)
def dexscreener_search(query: str) -> list:
    try:
        r = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={query}", timeout=10)
        if r.status_code == 200:
            return r.json().get("pairs", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=60)
def dexscreener_pair(chain_id: str, pair_address: str):
    try:
        r = requests.get(f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("pairs"):
                return data["pairs"][0]
    except Exception:
        pass
    return None

# ── Risk scoring ──
def calculate_risk(pair_info: dict):
    score = 50
    signals = []
    if not pair_info:
        return score, [("Pas de données", "medium")]

    mcap = pair_info.get("marketCap", 0) or 0
    fdv = pair_info.get("fdv", 0) or 0
    liq = pair_info.get("liquidity", {}).get("usd", 0) or 0
    vol_24h = pair_info.get("volume", {}).get("h24", 0) or 0
    chg_24h = pair_info.get("priceChange", {}).get("h24", 0) or 0
    pair_created = pair_info.get("pairCreatedAt", 0) or 0
    txns = pair_info.get("txns", {}).get("h24", {})
    buys = txns.get("buys", 0) or 0
    sells = txns.get("sells", 0) or 0
    info = pair_info.get("info", {})

    if mcap < 100_000: score += 15; signals.append(("Market cap <$100K", "high"))
    elif mcap < 500_000: score += 10; signals.append(("Low market cap (<$500K)", "medium"))
    elif mcap > 100_000_000: score -= 10; signals.append(("High market cap (>$100M)", "low"))
    elif mcap > 10_000_000: score -= 5; signals.append(("Solid market cap (>$10M)", "low"))

    if liq < 10_000: score += 20; signals.append(("CRITICAL: Liquidity <$10K", "high"))
    elif liq < 50_000: score += 15; signals.append(("Low liquidity (<$50K)", "medium"))
    elif liq < 200_000: score += 5; signals.append(("Moderate liquidity (<$200K)", "medium"))
    elif liq > 1_000_000: score -= 10; signals.append(("Strong liquidity (>$1M)", "low"))

    if liq > 0:
        ratio = vol_24h / liq
        if ratio > 10: score += 20; signals.append(("Vol/Liq >10x — pump & dump", "high"))
        elif ratio > 5: score += 15; signals.append((f"Vol/Liq very high ({ratio:.1f}x)", "high"))
        elif ratio > 2: score += 8; signals.append((f"Elevated volume ({ratio:.1f}x liq)", "medium"))

    if chg_24h > 500: score += 15; signals.append(("Price up >500% — dump incoming", "high"))
    elif chg_24h > 200: score += 10; signals.append(("Price up >200%", "high"))
    elif chg_24h > 100: score += 5; signals.append(("Price up >100%", "medium"))
    elif chg_24h < -90: score += 15; signals.append(("Price down >90% — possible rug", "high"))
    elif chg_24h < -70: score += 10; signals.append(("Price down >70%", "medium"))

    if pair_created > 0:
        age_days = (time.time() * 1000 - pair_created) / (1000 * 86400)
        if age_days < 0.5: score += 20; signals.append(("CRITICAL: Token <12h old", "high"))
        elif age_days < 1: score += 15; signals.append(("Token <24h old", "high"))
        elif age_days < 7: score += 10; signals.append((f"Token {age_days:.0f}d old", "medium"))
        elif age_days < 30: score += 5; signals.append((f"Token {age_days:.0f}d old — young", "medium"))
        elif age_days > 365: score -= 10; signals.append((f"Token {age_days:.0f}d — established", "low"))
        elif age_days > 90: score -= 5; signals.append((f"Token {age_days:.0f}d — track record", "low"))

    total_tx = buys + sells
    if total_tx > 0:
        sell_ratio = sells / total_tx
        if sell_ratio > 0.8: score += 15; signals.append((f"Heavy selling ({sell_ratio*100:.0f}% sells)", "high"))
        elif sell_ratio > 0.6: score += 8; signals.append((f"More sells ({sell_ratio*100:.0f}%)", "medium"))
        elif sell_ratio < 0.2 and total_tx > 50: score -= 5; signals.append(("Strong buy pressure", "low"))

    if info:
        if not info.get("imageUrl"): score += 3; signals.append(("No token image", "medium"))
        if not info.get("socials"): score += 5; signals.append(("No social links", "low"))
        else: score -= 3; signals.append(("Social links present", "low"))
        if not info.get("websites"): score += 5; signals.append(("No website", "medium"))
        else: score -= 3; signals.append(("Website present", "low"))

    return max(0, min(100, score)), signals

def get_risk_label(score):
    if score <= 30: return "LOW", "#3fb950", "badge-risk-low"
    elif score <= 60: return "MEDIUM", "#d29922", "badge-risk-med"
    return "HIGH", "#f85149", "badge-risk-high"

# ── Demo tokens ──
if not search_query:
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>⚡ Démo rapide</div>", unsafe_allow_html=True)
    demo_tokens = {
        "SOL (Solana)": ("solana", "So11111111111111111111111111111111111111112"),
        "WIF (dogwifhat)": ("solana", "EKpQGSJtjMFqHFYzQ2RzBLH2K3cNoHGKutQYd2LQfC5X"),
        "BONK": ("solana", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"),
        "JUP (Jupiter)": ("solana", "JUPyiwrYJFskkApdCuW5Ys5CKiSRJDQ2p1BoBBU13wF"),
    }
    cols = st.columns(len(demo_tokens))
    for col, (label, (ch, addr)) in zip(cols, demo_tokens.items()):
        with col:
            if st.button(label, use_container_width=True, key=f"demo_{label}"):
                st.session_state["demo_chain"] = ch
                st.session_state["demo_addr"] = addr
                st.rerun()

    if "demo_addr" in st.session_state:
        with st.spinner("Analyse en cours..."):
            pair = dexscreener_pair(st.session_state["demo_chain"], st.session_state["demo_addr"])
            if pair:
                st.session_state["selected_pair"] = pair
                st.session_state["selected_name"] = st.session_state["demo_addr"][:8]
    st.markdown("</div>", unsafe_allow_html=True)

# ── Search execution ──
if search_query:
    with st.spinner(f"Recherche de '{search_query}' sur {chain}..."):
        results = dexscreener_search(f"{search_query} {chain}")

    if not results:
        pair = dexscreener_pair(chain, search_query)
        if pair:
            results = [pair]
        else:
            st.error("Token non found. Vérifie l'adresse ou essaie un autre terme.")

    if results and "selected_pair" not in st.session_state:
        st.markdown(f"<div class='rr-card'><div class='rr-card-title'>📋 {len(results)} résultat(s)</div>", unsafe_allow_html=True)
        for i, pair in enumerate(results[:5]):
            base = pair.get("baseToken", {})
            name = base.get("name", "Unknown")
            symbol = base.get("symbol", "???")
            pair_addr = pair.get("pairAddress", "")
            price = pair.get("priceUsd", "N/A")
            mcap = pair.get("marketCap", 0)
            score, _ = calculate_risk(pair)
            risk_lvl, risk_color, risk_cls = get_risk_label(score)

            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05);'>
              <div style='flex:1;'><strong>{name}</strong> <span style='color:#484f58;'>({symbol})</span><br>
              <span style='font-size:.75rem;color:#484f58;'>{pair_addr[:16]}...</span></div>
              <div style='text-align:right;'><strong>${price}</strong><br>
              <span style='font-size:.75rem;'>MCap: ${(mcap/1e6):.1f}M</span></div>
              <span class='{risk_cls}' style='min-width:60px;text-align:center;'>{risk_lvl} {score}</span>
            """, unsafe_allow_html=True)
            if st.button("Analyser", key=f"analyze_{i}"):
                st.session_state["selected_pair"] = pair
                st.session_state["selected_name"] = name
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ── Display analysis ──
if "selected_pair" in st.session_state:
    pair = st.session_state["selected_pair"]
    name = st.session_state.get("selected_name", "Token")
    score, signals = calculate_risk(pair)
    risk_lvl, risk_color, risk_cls = get_risk_label(score)
    base = pair.get("baseToken", {})

    st.write("")

    # ── Risk gauge + metrics ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)

    col_g, col_m1, col_m2, col_m3, col_m4 = st.columns([1.2, 1, 1, 1, 1])

    with col_g:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Risk Score", "font": {"color": "#484f58", "size": 11}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#30363d"},
                "bar": {"color": risk_color},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 30], "color": "rgba(63,185,80,0.12)"},
                    {"range": [30, 60], "color": "rgba(210,153,34,0.12)"},
                    {"range": [60, 100], "color": "rgba(248,81,73,0.12)"},
                ],
            },
            number={"font": {"color": risk_color, "size": 38}},
        ))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=35, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<div style='text-align:center;'><span class='{risk_cls}' style='font-size:1.1rem;'>{risk_lvl} RISK — {score}/100</span></div>", unsafe_allow_html=True)

    price = float(pair.get("priceUsd", 0) or 0)
    mcap = pair.get("marketCap", 0) or 0
    liq = pair.get("liquidity", {}).get("usd", 0) or 0
    vol = pair.get("volume", {}).get("h24", 0) or 0
    fdv = pair.get("fdv", 0) or 0

    fmt_price = f"${price:.8f}" if price < 0.01 else f"${price:.4f}" if price < 1 else f"${price:.2f}"
    fmt_mcap = f"${mcap/1e6:.1f}M" if mcap > 1e6 else f"${mcap/1e3:.0f}K" if mcap else "N/A"
    fmt_liq = f"${liq/1e3:.0f}K" if liq else "N/A"
    fmt_vol = f"${vol/1e3:.0f}K" if vol else "N/A"

    col_m1.metric("Prix", fmt_price)
    col_m2.metric("Market Cap", fmt_mcap)
    col_m3.metric("Liquidité", fmt_liq)
    col_m4.metric("Volume 24h", fmt_vol)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Signals ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>🚨 Signaux de manipulation</div>", unsafe_allow_html=True)

    high = [s for s, l in signals if l == "high"]
    medium = [s for s, l in signals if l == "medium"]
    low = [s for s, l in signals if l == "low"]

    if high:
        st.markdown("**🔴 Critique :**")
        for s in high:
            st.error(s)
    if medium:
        st.markdown("**🟡 Attention :**")
        for s in medium:
            st.warning(s)
    if low:
        st.markdown("**🟢 Positif :**")
        for s in low:
            st.success(s)
    if not high and not medium:
        st.success("🟢 Aucun signal de manipulation significatif détecté")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Token details ──
    st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
    st.markdown("<div class='rr-card-title'>📊 Détails du token</div>", unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        pair_created = pair.get("pairCreatedAt", 0) or 0
        age_days = (time.time() * 1000 - pair_created) / (1000 * 86400) if pair_created else 0
        details = {
            "FDV": f"${fdv/1e6:.1f}M" if fdv > 1e6 else f"${fdv/1e3:.0f}K" if fdv else "N/A",
            "Dex": pair.get("dexId", "Unknown"),
            "Pair": pair.get("pairAddress", "N/A")[:20] + "...",
            "Token": base.get("address", "N/A")[:20] + "...",
            "Âge": f"{age_days:.0f} jours" if age_days > 0 else "Inconnu",
            "Chain": pair.get("chainId", "Unknown"),
        }
        for k, v in details.items():
            st.write(f"**{k}:** `{v}`")

    with col_d2:
        pc = pair.get("priceChange", {})
        h24_txns = pair.get("txns", {}).get("h24", {})
        metrics = {
            "5min": f"{pc.get('m5', 0):.1f}%",
            "1h": f"{pc.get('h1', 0):.1f}%",
            "6h": f"{pc.get('h6', 0):.1f}%",
            "24h": f"{pc.get('h24', 0):.1f}%",
            "Buys 24h": str(h24_txns.get("buys", 0)),
            "Sells 24h": str(h24_txns.get("sells", 0)),
        }
        for k, v in metrics.items():
            st.write(f"**{k}:** {v}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Socials ──
    info = pair.get("info", {})
    if info:
        st.markdown("<div class='rr-card'>", unsafe_allow_html=True)
        st.markdown("<div class='rr-card-title'>🔗 Liens & Réseaux</div>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            websites = info.get("websites", [])
            if websites:
                for w in websites[:3]:
                    url = w.get("url", w) if isinstance(w, dict) else w
                    st.write(f"🌐 {url}")
            else:
                st.write("Pas de site web")
        with col_s2:
            socials = info.get("socials", [])
            if socials:
                for s in socials[:5]:
                    st.write(f"{s.get('type', 'Link')}: {s.get('url', s) if isinstance(s, dict) else s}")
            else:
                st.write("Pas de réseaux sociaux")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Raw JSON ──
    with st.expander("📋 Données brutes (JSON)"):
        st.json(pair)

    # ── Clear button ──
    if st.button("🔄 Nouvelle analyse"):
        del st.session_state["selected_pair"]
        if "selected_name" in st.session_state:
            del st.session_state["selected_name"]
        if "demo_addr" in st.session_state:
            del st.session_state["demo_addr"]
        st.rerun()

disclaimer()
