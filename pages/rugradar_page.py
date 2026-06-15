import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import time

# ─── DEXSCREENER API (no key needed) ────────────────────────────────────────
@st.cache_data(ttl=60)
def dexscreener_search(query):
    """Search tokens on DexScreener"""
    url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("pairs", [])
    except:
        pass
    return []

@st.cache_data(ttl=60)
def dexscreener_pair(chain_id, pair_address):
    """Get pair data from DexScreener"""
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("pairs"):
                return data["pairs"][0]
    except:
        pass
    return None

@st.cache_data(ttl=60)
def dexscreener_token(chain_id, token_address):
    """Get token data from DexScreener"""
    url = f"https://api.dexscreener.com/tokens/v1/{chain_id}/{token_address}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data and len(data) > 0:
                return data[0]
    except:
        pass
    return None

# ─── COINGECKO API (no key needed) ──────────────────────────────────────────
@st.cache_data(ttl=60)
def coingecko_search(query):
    """Search coins on CoinGecko"""
    url = "https://api.coingecko.com/api/v3/search"
    try:
        r = requests.get(url, params={"query": query}, timeout=10)
        if r.status_code == 200:
            return r.json().get("coins", [])
    except:
        pass
    return []

@st.cache_data(ttl=60)
def coingecko_details(coin_id):
    """Get coin details from CoinGecko"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "true",
        "developer_data": "false",
        "sparkline": "false",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

@st.cache_data(ttl=120)
def coingecko_top_coins(per_page=50):
    """Get top coins from CoinGecko"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

@st.cache_data(ttl=120)
def coingecko_trending():
    """Get trending coins from CoinGecko"""
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("coins", [])
    except:
        pass
    return []

@st.cache_data(ttl=120)
def coingecko_fear_greed():
    """Get Fear & Greed index"""
    url = "https://api.alternative.me/fng/"
    try:
        r = requests.get(url, params={"limit": 1}, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return data[0]
    except:
        pass
    return None

# ─── RISK SCORING ────────────────────────────────────────────────────────────
def calculate_risk(pair_info):
    """
    Calculate risk score 0-100 based on DexScreener data
    0-30 = Low (green) | 31-60 = Medium (orange) | 61-100 = High (red)
    """
    score = 50
    signals = []

    if not pair_info:
        return score, ["No pair data available"]

    # ── Market Cap ──
    mcap = pair_info.get("marketCap", 0) or 0
    fdv = pair_info.get("fdv", 0) or 0

    if mcap < 100000:
        score += 15
        signals.append(("CRITICAL: Market cap <$100K — extreme manipulation risk", "high"))
    elif mcap < 500000:
        score += 10
        signals.append(("Low market cap (<$500K) — vulnerable to dumps", "medium"))
    elif mcap > 100000000:
        score -= 10
        signals.append(("High market cap (>$100M) — lower manipulation probability", "low"))
    elif mcap > 10000000:
        score -= 5
        signals.append(("Solid market cap (>$10M) — moderate stability", "low"))

    # ── Liquidity ──
    liquidity = pair_info.get("liquidity", {})
    liq_usd = liquidity.get("usd", 0) or 0
    liq_base = liquidity.get("base", 0) or 0

    if liq_usd < 10000:
        score += 20
        signals.append(("CRITICAL: Liquidity <$10K — extremely easy to manipulate", "high"))
    elif liq_usd < 50000:
        score += 15
        signals.append(("Low liquidity (<$50K) — vulnerable to rug pulls", "medium"))
    elif liq_usd < 200000:
        score += 5
        signals.append(("Moderate liquidity (<$200K) — could be manipulated", "medium"))
    elif liq_usd > 1000000:
        score -= 10
        signals.append(("Strong liquidity (>$1M) — harder to manipulate", "low"))

    # ── Volume / Liquidity Ratio ──
    volume = pair_info.get("volume", {})
    vol_24h = volume.get("h24", 0) or 0
    vol_6h = volume.get("h6", 0) or 0
    vol_1h = volume.get("h1", 0) or 0

    if liq_usd > 0:
        vol_liq_ratio = vol_24h / liq_usd
        if vol_liq_ratio > 10:
            score += 20
            signals.append(("CRITICAL: Volume/Liquidity ratio >10x — classic pump & dump pattern", "high"))
        elif vol_liq_ratio > 5:
            score += 15
            signals.append(("Volume/Liquidity ratio very high ({:.1f}x) — possible pump incoming".format(vol_liq_ratio), "high"))
        elif vol_liq_ratio > 2:
            score += 8
            signals.append(("Elevated volume ({:.1f}x liquidity) — monitor closely".format(vol_liq_ratio), "medium"))
        elif vol_liq_ratio < 0.05:
            score += 5
            signals.append(("Very low volume — illiquid, hard to exit", "medium"))

    # ── Price Change ──
    price_change = pair_info.get("priceChange", {})
    chg_24h = price_change.get("h24", 0) or 0
    chg_5m = price_change.get("m5", 0) or 0

    if chg_24h > 500:
        score += 15
        signals.append(("Price up >500% in 24h — extreme pump, dump likely incoming", "high"))
    elif chg_24h > 200:
        score += 10
        signals.append(("Price up >200% in 24h — possible pump, be very careful", "high"))
    elif chg_24h > 100:
        score += 5
        signals.append(("Price up >100% in 24h — strong momentum but watch for reversal", "medium"))
    elif chg_24h < -90:
        score += 15
        signals.append(("Price down >90% — possible rug or panic sell", "high"))
    elif chg_24h < -70:
        score += 10
        signals.append(("Price down >70% — heavy selling pressure", "medium"))

    # ── Token Age ──
    pair_created = pair_info.get("pairCreatedAt", 0) or 0
    if pair_created > 0:
        age_days = (time.time() * 1000 - pair_created) / (1000 * 86400)
        if age_days < 0.5:
            score += 20
            signals.append(("CRITICAL: Token created less than 12h ago — extreme risk", "high"))
        elif age_days < 1:
            score += 15
            signals.append(("Token created less than 24h ago — very high risk", "high"))
        elif age_days < 7:
            score += 10
            signals.append(("Token only {:.0f} days old — new, high risk".format(age_days), "medium"))
        elif age_days < 30:
            score += 5
            signals.append(("Token is {:.0f} days old — still young".format(age_days), "medium"))
        elif age_days > 365:
            score -= 10
            signals.append(("Token is {:.0f} days old — established, lower risk".format(age_days), "low"))
        elif age_days > 90:
            score -= 5
            signals.append(("Token is {:.0f} days old — moderate track record".format(age_days), "low"))

    # ── Buy/Sell Ratio ──
    txns = pair_info.get("txns", {})
    h24_txns = txns.get("h24", {})
    buys_24h = h24_txns.get("buys", 0) or 0
    sells_24h = h24_txns.get("sells", 0) or 0
    total_txns = buys_24h + sells_24h

    if total_txns > 0:
        sell_ratio = sells_24h / total_txns
        if sell_ratio > 0.8:
            score += 15
            signals.append(("Heavy selling pressure ({:.0f}% sells) — possible dump incoming".format(sell_ratio*100), "high"))
        elif sell_ratio > 0.6:
            score += 8
            signals.append(("More sells than buys ({:.0f}% sells) — watch closely".format(sell_ratio*100), "medium"))
        elif sell_ratio < 0.2 and total_txns > 50:
            score -= 5
            signals.append(("Strong buy pressure ({:.0f}% buys)".format((1-sell_ratio)*100), "low"))

    # ── Info / Socials ──
    info = pair_info.get("info", {})
    if info:
        socials = info.get("socials", [])
        websites = info.get("websites", [])
        image = info.get("imageUrl")

        if not image:
            score += 3
            signals.append(("No token image — low effort project", "medium"))
        if not socials:
            score += 5
            signals.append(("No social links — anonymous team risk", "medium"))
        else:
            score -= 3
            signals.append(("Social links present — some transparency", "low"))
        if not websites:
            score += 5
            signals.append(("No website — anonymous project", "medium"))
        else:
            score -= 3
            signals.append(("Website present — some legitimacy", "low"))

    # ── Price USD sanity check ──
    price_usd = float(pair_info.get("priceUsd", 0) or 0)
    if price_usd > 0 and price_usd < 0.000001:
        score += 5
        signals.append(("Extremely low token price — likely micro-cap manipulation", "medium"))

    # ── Clamp ──
    score = max(0, min(100, score))
    return score, signals

def get_risk_level(score):
    if score <= 30:
        return "LOW", "#3fb950"
    elif score <= 60:
        return "MEDIUM", "#d29922"
    else:
        return "HIGH", "#f85149"

# ─── PAGE ─────────────────────────────────────────────────────────────────────
LOGO = "https://user-gen-media-assets.s3.amazonaws.com/gemini_images/2877ac40-2405-4447-b8a8-4526ddbadd72.png"

st.set_page_config(page_title="RugRadar — Manipulation Detector", page_icon="🔍", layout="wide")

st.markdown("""
<style>
.stApp { background: #0b1020; }
.header-wrap{display:flex;align-items:center;gap:14px;margin-bottom:1rem;padding:6px 0 10px 0;}
.header-img{width:54px;height:54px;border-radius:16px;object-fit:cover;box-shadow:0 4px 14px rgba(0,0,0,.28);flex-shrink:0;}
.header-title{font-size:2.15rem;font-weight:800;line-height:1.05;color:#fff;}
.card{padding:1rem 1.05rem;border-radius:18px;border:1px solid rgba(255,255,255,.08);background:linear-gradient(180deg, rgba(18,23,38,.96), rgba(10,14,24,.96));box-shadow:0 10px 32px rgba(0,0,0,.18);}
.risk-box{padding:1.5rem;border-radius:16px;text-align:center;border:2px solid;}
.signal-item{padding:8px 12px;border-radius:8px;margin:4px 0;font-size:0.92em;}
.disclaimer{background:rgba(210,153,34,0.08);border-left:4px solid #d29922;padding:12px 16px;border-radius:4px;font-size:0.85em;color:#8b949e;}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──
col_menu, col_title = st.columns([1, 8])
with col_menu:
    if st.button("Menu", use_container_width=True):
        st.switch_page("main.py")
with col_title:
    st.markdown(f"""
    <div class="header-wrap">
        <img class="header-img" src="{LOGO}">
        <div class="header-title">RugRadar</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Crypto Manipulation Detector — Know When to Exit")

st.markdown("""
<div class="disclaimer">
⚠️ <strong>DISCLAIMER:</strong> RugRadar is an analysis tool, NOT financial advice.
All data is indicative. Always do your own research. Crypto investments carry total loss risk.
</div>
""", unsafe_allow_html=True)

st.write("")

# ─── SEARCH ──
search_query = st.text_input(
    "🔎 Search Token",
    placeholder="Token name, symbol, or contract address (e.g., WIF, SOL, or 0x...)"
)

chain = st.selectbox("Chain", ["solana", "ethereum", "bsc", "base", "arbitrum"], index=0)

st.write("")

# ─── DEMO MODE ──
if not search_query:
    st.info("👆 Search for any token above, or try a demo below")

    demo_tokens = {
        "SOL (Solana)": ("solana", "So11111111111111111111111111111111111111112"),
        "WIF (dogwifhat)": ("solana", "EKpQGSJtjMFqHFYzQ2RzBLH2K3cNoHGKutQYd2LQfC5X"),
        "BONK": ("solana", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"),
        "JUP (Jupiter)": ("solana", "JUPyiwrYJFskkApdCuW5Ys5CKiSRJDQ2p1BoBBU13wF"),
    }

    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        selected_demo = st.selectbox("Quick Demo", list(demo_tokens.keys()))
    with col_demo2:
        st.write("")
        st.write("")
        run_demo = st.button("🔍 Analyze", use_container_width=True, type="primary")

    if run_demo:
        chain_id, token_addr = demo_tokens[selected_demo]
        with st.spinner(f"Analyzing {selected_demo}..."):
            pair_data = dexscreener_pair(chain_id, token_addr)
            if not pair_data:
                # Try token search
                results = dexscreener_search(f"{selected_demo} {chain_id}")
                if results:
                    pair_data = results[0]

        if pair_data:
            display_rugradar(pair_data, selected_demo)
        else:
            st.error("Could not fetch data. Try searching directly.")
    st.stop()

# ─── SEARCH MODE ──
with st.spinner(f"Searching '{search_query}' on {chain}..."):
    results = dexscreener_search(f"{search_query} {chain}")

if not results:
    # Try as direct address
    with st.spinner("Trying direct address lookup..."):
        pair_data = dexscreener_pair(chain, search_query)
        if pair_data:
            token_name = pair_data.get("baseToken", {}).get("name", "Unknown")
            display_rugradar(pair_data, token_name)
        else:
            st.error("Token not found. Check the contract address or try another search.")
    st.stop()

# ─── SHOW RESULTS ──
st.subheader(f"Found {len(results)} result(s)")

for i, pair in enumerate(results[:5]):
    base = pair.get("baseToken", {})
    name = base.get("name", "Unknown")
    symbol = base.get("symbol", "???")
    pair_addr = pair.get("pairAddress", "")
    price = pair.get("priceUsd", "N/A")
    mcap = pair.get("marketCap", 0)

    col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
    with col_a:
        st.markdown(f"**{name}** ({symbol})")
        st.caption(f"`{pair_addr[:20]}...`" if len(pair_addr) > 20 else f"`{pair_addr}`")
    with col_b:
        st.markdown(f"Price: ${price}")
    with col_c:
        st.markdown(f"MCap: ${(mcap/1e6):.1f}M" if mcap and mcap > 1e6 else f"MCap: ${(mcap/1e3):.0f}K" if mcap else "N/A")
    with col_d:
        if st.button("Analyze", key=f"analyze_{i}", type="primary"):
            st.session_state["selected_pair"] = pair
            st.rerun()

if "selected_pair" in st.session_state:
    pair = st.session_state["selected_pair"]
    token_name = pair.get("baseToken", {}).get("name", "Unknown")
    display_rugradar(pair, token_name)

# ─── DISPLAY FUNCTION ────────────────────────────────────────────────────────
def display_rugradar(pair_info, token_name):
    """Full RugRadar analysis display"""
    score, signals = calculate_risk(pair_info)
    risk_level, risk_color = get_risk_level(score)

    # ── Header ──
    st.write("")
    base = pair_info.get("baseToken", {})
    st.markdown(f"## 🔍 {token_name} ({base.get('symbol', '???')})")
    st.write("")

    # ── Risk Score + Metrics ──
    col_risk, col_m1, col_m2, col_m3, col_m4 = st.columns([1.2, 1, 1, 1, 1])

    with col_risk:
        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Risk Score", "font": {"color": "#8b949e", "size": 12}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#30363d"},
                "bar": {"color": risk_color},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 30], "color": "rgba(63,185,80,0.15)"},
                    {"range": [30, 60], "color": "rgba(210,153,34,0.15)"},
                    {"range": [60, 100], "color": "rgba(248,81,73,0.15)"},
                ],
            },
            number={"font": {"color": risk_color, "size": 42}},
        ))
        fig.update_layout(
            height=220,
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Risk label
        st.markdown(f"""
        <div style="text-align:center;padding:8px;border-radius:12px;border:2px solid {risk_color};background:rgba(0,0,0,0.3);">
            <span style="color:{risk_color};font-size:1.3em;font-weight:800;">{risk_level} RISK</span>
        </div>
        """, unsafe_allow_html=True)

    # Metrics
    price = float(pair_info.get("priceUsd", 0) or 0)
    mcap = pair_info.get("marketCap", 0) or 0
    liq = pair_info.get("liquidity", {}).get("usd", 0) or 0
    vol_24h = pair_info.get("volume", {}).get("h24", 0) or 0
    fdv = pair_info.get("fdv", 0) or 0

    col_m1.metric("Price", f"${price:.8f}" if price < 0.01 else f"${price:.4f}" if price < 1 else f"${price:.2f}")
    col_m2.metric("Market Cap", f"${mcap/1e6:.1f}M" if mcap > 1e6 else f"${mcap/1e3:.0f}K" if mcap else "N/A")
    col_m3.metric("Liquidity", f"${liq/1e3:.0f}K" if liq else "N/A")
    col_m4.metric("24h Volume", f"${vol_24h/1e3:.0f}K" if vol_24h else "N/A")

    st.write("")

    # ── Manipulation Signals ──
    st.subheader("🚨 Manipulation Signals")

    high_risks = [s for s, level in signals if level == "high"]
    medium_risks = [s for s, level in signals if level == "medium"]
    low_risks = [s for s, level in signals if level == "low"]

    if high_risks:
        for s in high_risks:
            st.error(f"🔴 {s}")
    if medium_risks:
        for s in medium_risks:
            st.warning(f"🟡 {s}")
    if low_risks:
        for s in low_risks:
            st.success(f"🟢 {s}")

    if not high_risks and not medium_risks:
        st.success("🟢 No significant manipulation signals detected")

    st.write("")

    # ── Token Details ──
    col_details1, col_details2 = st.columns(2)

    with col_details1:
        st.subheader("📊 Token Details")
        pair_created = pair_info.get("pairCreatedAt", 0) or 0
        age_days = (time.time() * 1000 - pair_created) / (1000 * 86400) if pair_created else 0

        details = {
            "FDV": f"${fdv/1e6:.1f}M" if fdv > 1e6 else f"${fdv/1e3:.0f}K" if fdv else "N/A",
            "Dex": pair_info.get("dexId", "Unknown"),
            "Pair Address": pair_info.get("pairAddress", "N/A")[:20] + "...",
            "Token Address": base.get("address", "N/A")[:20] + "...",
            "Age": f"{age_days:.0f} days" if age_days > 0 else "Unknown",
            "Chain": pair_info.get("chainId", "Unknown"),
        }

        for k, v in details.items():
            st.write(f"**{k}:** {v}")

    with col_details2:
        st.subheader("📈 Price Action")
        price_change = pair_info.get("priceChange", {})
        txns = pair_info.get("txns", {})

        metrics = {
            "5min Change": f"{price_change.get('m5', 0):.1f}%",
            "1h Change": f"{price_change.get('h1', 0):.1f}%",
            "6h Change": f"{price_change.get('h6', 0):.1f}%",
            "24h Change": f"{price_change.get('h24', 0):.1f}%",
            "24h Buys": str(txns.get("h24", {}).get("buys", 0)),
            "24h Sells": str(txns.get("h24", {}).get("sells", 0)),
        }

        for k, v in metrics.items():
            st.write(f"**{k}:** {v}")

    st.write("")

    # ── Social / Info ──
    info = pair_info.get("info", {})
    if info:
        st.subheader("🔗 Social & Info")
        col_soc1, col_soc2 = st.columns(2)
        with col_soc1:
            websites = info.get("websites", [])
            if websites:
                for w in websites[:3]:
                    st.write(f"Website: {w.get('url', w) if isinstance(w, dict) else w}")
            else:
                st.write("No website found")
        with col_soc2:
            socials = info.get("socials", [])
            if socials:
                for s in socials[:5]:
                    st.write(f"{s.get('type', 'Link')}: {s.get('url', s) if isinstance(s, dict) else s}")
            else:
                st.write("No social links found")

    st.write("")

    # ── Raw Data ──
    with st.expander("📋 Raw Pair Data (JSON)"):
        st.json(pair_info)

    st.write("")
    st.markdown("""
    <div class="disclaimer">
    ⚠️ This analysis uses DexScreener data only. For complete on-chain analysis
    (contract verification, liquidity lock, top holder wallets), integrate Helius or Moralis API.
    Always DYOR.
    </div>
    """, unsafe_allow_html=True)
