"""
RugRadar — Shared CSS & utilities
Import this at the top of every page for consistent styling.
"""
import streamlit as st

LOGO = "assets/rugradar_logo.png"

def apply_style():
    st.markdown("""
    <style>
    .stApp { background: #0a0e1a; }
    section[data-testid="stSidebar"] { background: #080c16; border-right: 1px solid rgba(255,255,255,.06); }

    /* ── Global ── */
    h1, h2, h3, h4 { color: #e6edf3 !important; }
    .stCaption { color: #484f58 !important; }

    /* ── Header ── */
    .rr-header{display:flex;align-items:center;gap:12px;margin-bottom:1rem;padding:8px 0 14px 0;border-bottom:1px solid rgba(255,255,255,.06);}
    .rr-logo{width:44px;height:44px;border-radius:12px;object-fit:cover;box-shadow:0 2px 12px rgba(0,0,0,.4);flex-shrink:0;}
    .rr-title{font-size:1.6rem;font-weight:800;color:#fff;line-height:1;letter-spacing:-.01em;}
    .rr-sub{font-size:.8rem;color:#484f58;margin-top:1px;}

    /* ── Cards ── */
    .rr-card{padding:1rem 1.1rem;border-radius:14px;border:1px solid rgba(255,255,255,.07);
            background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,.01));
            box-shadow:0 4px 20px rgba(0,0,0,.15);margin-bottom:.8rem;}
    .rr-card-title{font-size:.95rem;font-weight:700;color:#c9d1d9;margin-bottom:.5rem;display:flex;align-items:center;gap:6px;}

    /* ── Signal badges ── */
    .badge-buy{display:inline-block;padding:3px 10px;border-radius:6px;background:rgba(34,197,94,.15);color:#3fb950;font-weight:700;font-size:.78rem;}
    .badge-sell{display:inline-block;padding:3px 10px;border-radius:6px;background:rgba(239,68,68,.15);color:#f85149;font-weight:700;font-size:.78rem;}
    .badge-wait{display:inline-block;padding:3px 10px;border-radius:6px;background:rgba(210,153,34,.15);color:#d29922;font-weight:700;font-size:.78rem;}
    .badge-risk-low{display:inline-block;padding:2px 8px;border-radius:4px;background:rgba(63,185,80,.12);color:#3fb950;font-weight:600;font-size:.72rem;}
    .badge-risk-med{display:inline-block;padding:2px 8px;border-radius:4px;background:rgba(210,153,34,.12);color:#d29922;font-weight:600;font-size:.72rem;}
    .badge-risk-high{display:inline-block;padding:2px 8px;border-radius:4px;background:rgba(248,81,73,.12);color:#f85149;font-weight:600;font-size:.72rem;}

    /* ── Metric row ── */
    .metric-row{display:flex;gap:8px;flex-wrap:wrap;margin:.5rem 0;}
    .metric-pill{padding:6px 14px;border-radius:10px;background:rgba(255,255,255,.04);
                border:1px solid rgba(255,255,255,.07);text-align:center;min-width:80px;}
    .metric-pill .val{font-size:1.1rem;font-weight:800;color:#e6edf3;}
    .metric-pill .lbl{font-size:.65rem;color:#484f58;text-transform:uppercase;letter-spacing:.05em;}

    /* ── Disclaimer ── */
    .rr-disclaimer{background:rgba(210,153,34,0.05);border-left:3px solid #d29922;
                  padding:8px 12px;border-radius:0 6px 6px 0;font-size:.78rem;color:#484f58;margin-top:1rem;}

    /* ── Locked overlay ── */
    .locked-overlay{position:relative;}
    .locked-overlay::after{content:'🔒 Premium requis';position:absolute;inset:0;background:rgba(10,14,26,.85);
                          display:flex;align-items:center;justify-content:center;border-radius:14px;
                          color:#fbbf24;font-weight:700;font-size:1rem;backdrop-filter:blur(2px);}

    /* ── Animations ── */
    @keyframes pulse-green { 0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,0);} 50%{box-shadow:0 0 12px 2px rgba(34,197,94,.2);} }
    .pulse-green { animation: pulse-green 2s infinite; }
    </style>
    """, unsafe_allow_html=True)

def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="rr-header">
      <img class="rr-logo" src="{LOGO}">
      <div>
        <div class="rr-title">{title}</div>
        {f'<div class="rr-sub">{subtitle}</div>' if subtitle else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)

def disclaimer():
    st.markdown("""
    <div class="rr-disclaimer">
    ⚠️ RugRadar est un outil d'analyse, PAS un conseil financier. Toujours DYOR. Crypto = risque de perte totale.
    </div>
    """, unsafe_allow_html=True)

def plan_gate(min_tier: str = "pro"):
    """Block content if user's plan is below min_tier. Call at top of gated pages."""
    if "user_plan" not in st.session_state:
        st.session_state["user_plan"] = "free"
    plan = st.session_state["user_plan"]
    tier = {"free": 0, "pro": 1, "ultimate": 2}
    if tier.get(plan, 0) < tier.get(min_tier, 1):
        st.warning(f"🔒 Cette page nécessite le plan **{min_tier.upper()}** ou supérieur.")
        st.info("Passe au plan supérieur pour débloquer cette fonctionnalité.")
        if st.button(f"⚡ Voir les offres", type="primary"):
            st.switch_page("pages/prenium_page.py")
        st.stop()
