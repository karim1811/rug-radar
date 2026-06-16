import streamlit as st

from utils import apply_style, LOGO

apply_style()

st.set_page_config(page_title="RugRadar Premium", page_icon=LOGO, layout="wide")

st.markdown("""
<style>
.stApp { background: #0b1020; }
.header-wrap{display:flex;align-items:center;gap:14px;margin-bottom:1rem;padding:6px 0 10px 0;}
.header-img{width:54px;height:54px;border-radius:16px;object-fit:cover;box-shadow:0 4px 14px rgba(0,0,0,.28);flex-shrink:0;}
.header-title{font-size:2.15rem;font-weight:800;line-height:1.05;color:#fff;}
.card{padding:1rem 1.05rem;border-radius:18px;border:1px solid rgba(255,255,255,.08);background:linear-gradient(180deg, rgba(18,23,38,.96), rgba(10,14,24,.96));box-shadow:0 10px 32px rgba(0,0,0,.18);}
.card-locked{opacity:.55;pointer-events:none;position:relative;}
.card-locked::after{content:'🔒 Nécessite ce plan';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:1.1rem;font-weight:700;color:#fbbf24;background:rgba(0,0,0,.7);padding:8px 16px;border-radius:10px;white-space:nowrap;}
.badge{display:inline-block;padding:.25rem .6rem;border-radius:999px;background:rgba(234,179,8,.15);color:#fbbf24;font-weight:700;font-size:.82rem;}
.price{font-size:2rem;font-weight:900;margin:.2rem 0 .5rem 0;}
.feature{display:flex;align-items:center;gap:8px;padding:6px 0;font-size:.95em;color:#c9d1d9;}
.feature-disabled{color:#484f58;}
.faq-item{padding:12px 0;border-bottom:1px solid rgba(255,255,255,.06);}
.faq-q{font-weight:700;color:#e6edf3;font-size:.98rem;}
.faq-a{color:#8b949e;font-size:.9rem;margin-top:4px;}
.upgrade-banner{padding:14px 18px;border-radius:14px;border:1px solid rgba(234,179,8,.25);background:linear-gradient(135deg,rgba(234,179,8,.08),rgba(139,92,246,.06));display:flex;align-items:center;justify-content:space-between;gap:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-wrap">
  <img class="header-img" src="{LOGO}">
  <div class="header-title">RugRadar Premium</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 8])
with col1:
    if st.button("Menu", use_container_width=True):
        st.switch_page("main.py")
with col2:
    st.markdown("<span class='badge'>⭐ OFFRE PREMIUM</span>", unsafe_allow_html=True)
    st.markdown("### Débloque tout le potentiel de RugRadar")

st.write("")

# ── Plan detection ──
# In a real app this comes from a DB / auth. Here we use session_state.
if "user_plan" not in st.session_state:
    st.session_state["user_plan"] = "free"  # free | pro | ultimate

plan = st.session_state["user_plan"]
plan_labels = {"free": "🆓 Gratuit", "pro": "⚡ Pro", "ultimate": "💎 Ultimate"}
st.info(f"Ton plan actuel : **{plan_labels.get(plan, 'Gratuit')}**")

st.write("")

# ── Plans ──
st.subheader("Nos offres")
p1, p2, p3 = st.columns(3)

with p1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("#### 🆓 Gratuit")
    st.markdown("<div class='price'>0€<span style='font-size:.9rem;font-weight:400;color:#8b949e;'>/mois</span></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='feature'>✅ Scanner de tokens</div>
    <div class='feature'>✅ Watchlist basique (4 tokens)</div>
    <div class='feature'>✅ Données marché</div>
    <div class='feature feature-disabled'>❌ Signaux avancés</div>
    <div class='feature feature-disabled'>❌ Alertes temps réel</div>
    <div class='feature feature-disabled'>❌ Support prioritaire</div>
    """, unsafe_allow_html=True)
    if plan == "free":
        st.button("✅ Plan actuel", disabled=True, use_container_width=True, key="plan_free")
    else:
        st.button("Revenir au gratuit", use_container_width=True, key="downgrade_free")
    st.markdown("</div>", unsafe_allow_html=True)

with p2:
    border = "rgba(234,179,8,.4)" if plan == "pro" else "rgba(234,179,8,.2)"
    st.markdown(f"<div class='card' style='border-color:{border};'>", unsafe_allow_html=True)
    st.markdown("#### ⚡ Pro")
    st.markdown("<div class='price'>9.99€<span style='font-size:.9rem;font-weight:400;color:#8b949e;'>/mois</span></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='feature'>✅ Tout le gratuit</div>
    <div class='feature'>✅ Signaux avancés</div>
    <div class='feature'>✅ Alertes Telegram</div>
    <div class='feature'>✅ Watchlist illimitée</div>
    <div class='feature'>✅ Support prioritaire</div>
    <div class='feature feature-disabled'>❌ API access</div>
    <div class='feature feature-disabled'>❌ Alertes webhook</div>
    <div class='feature feature-disabled'>❌ Analyse on-chain Helius</div>
    <div class='feature feature-disabled'>❌ Détection whale moves</div>
    """, unsafe_allow_html=True)
    if plan == "pro":
        st.button("✅ Plan actuel", disabled=True, use_container_width=True, key="plan_pro")
    elif plan == "ultimate":
        st.button("Rétrograder vers Pro", use_container_width=True, key="downgrade_pro")
    else:
        if st.button("🚀 Passer Pro", use_container_width=True, type="primary", key="upgrade_pro"):
            st.session_state["user_plan"] = "pro"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with p3:
    border = "rgba(139,92,246,.4)" if plan == "ultimate" else "rgba(139,92,246,.2)"
    st.markdown(f"<div class='card' style='border-color:{border};'>", unsafe_allow_html=True)
    st.markdown("#### 💎 Ultimate")
    st.markdown("<div class='price'>24.99€<span style='font-size:.9rem;font-weight:400;color:#8b949e;'>/mois</span></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='feature'>✅ Tout le Pro</div>
    <div class='feature'>✅ API access</div>
    <div class='feature'>✅ Alertes webhook</div>
    <div class='feature'>✅ Analyse on-chain Helius</div>
    <div class='feature'>✅ Détection whale moves</div>
    <div class='feature'>✅ Support 24/7</div>
    """, unsafe_allow_html=True)
    if plan == "ultimate":
        st.button("✅ Plan actuel", disabled=True, use_container_width=True, key="plan_ultimate")
    else:
        if st.button("💎 Passer Ultimate", use_container_width=True, type="primary", key="upgrade_ultimate"):
            st.session_state["user_plan"] = "ultimate"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ── Feature access matrix ──
st.subheader("📋 Ce à quoi tu as accès")

features = [
    ("Scanner de tokens", "free", "🔍"),
    ("Watchlist basique (4 tokens)", "free", "📋"),
    ("Données marché live", "free", "📊"),
    ("Signaux avancés", "pro", "🚨"),
    ("Alertes Telegram", "pro", "📱"),
    ("Watchlist illimitée", "pro", "📋"),
    ("Support prioritaire", "pro", "💬"),
    ("API access", "ultimate", "🔌"),
    ("Alertes webhook", "ultimate", "🔗"),
    ("Analyse on-chain Helius", "ultimate", "⛓️"),
    ("Détection whale moves", "ultimate", "🐋"),
    ("Support 24/7", "ultimate", "🆘"),
]

tier_level = {"free": 0, "pro": 1, "ultimate": 2}

f1, f2 = st.columns(2)
for i, (feature, required_tier, icon) in enumerate(features):
    col = f1 if i % 2 == 0 else f2
    has_access = tier_level[plan] >= tier_level[required_tier]
    lock_icon = "✅" if has_access else "🔒"
    color = "#c9d1d9" if has_access else "#484f58"
    with col:
        st.markdown(f"<div style='display:flex;align-items:center;gap:8px;padding:6px 0;'>"
                    f"<span>{lock_icon}</span>"
                    f"<span style='color:{color};'>{icon} {feature}</span>"
                    f"<span style='margin-left:auto;font-size:.75rem;color:#8b949e;'>{required_tier.upper()}</span>"
                    f"</div>", unsafe_allow_html=True)

st.write("")

# ── Locked features CTA ──
if plan != "ultimate":
    locked_features = [f for f, t, _ in features if tier_level[t] > tier_level[plan]]
    st.markdown(f"""
    <div class='upgrade-banner'>
        <div>
            <strong style='color:#fbbf24;'>🔒 {len(locked_features)} fonctionnalités verrouillées</strong><br>
            <span style='color:#8b949e;font-size:.85rem;'>Passe au plan supérieur pour débloquer tout.</span>
        </div>
    """, unsafe_allow_html=True)
    if plan == "free":
        if st.button("⚡ Passer Pro", key="cta_pro", type="primary"):
            st.session_state["user_plan"] = "pro"
            st.rerun()
    if st.button("💎 Passer Ultimate", key="cta_ultimate"):
        st.session_state["user_plan"] = "ultimate"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ── FAQ ──
st.subheader("FAQ")

faq = [
    ("Comment fonctionne le premium ?",
     "Après paiement, tu reçois un accès aux fonctionnalités avancées : signaux de trading automatiques, alertes Telegram en temps réel, et une watchlist illimitée. Le plan Ultimate ajoute l'accès API, les alertes webhook et l'analyse on-chain."),
    ("Quels moyens de paiement ?",
     "Carte bancaire via Stripe. Bientôt PayPal et crypto."),
    ("Puis-je annuler à tout moment ?",
     "Oui, pas d'engagement. Tu peux annuler ou changer de plan à tout moment."),
    ("C'est quoi les signaux avancés ?",
     "Des alertes basées sur l'analyse de risque RugRadar + des patterns de manipulation détectés en temps réel. Disponible à partir du plan Pro."),
    ("C'est quoi la détection whale moves ?",
     "On surveille les gros mouvements de baleines (wallets importants) sur les tokens de ta watchlist. Seulement disponible en Ultimate."),
    ("Y a-t-il un essai gratuit ?",
     "Le plan Gratuit est illimité dans le temps. Tu peux tester le scanner et les données marché sans payer."),
]

for q, a in faq:
    with st.expander(f"❓ {q}"):
        st.write(a)

st.write("")
st.markdown("""
<div style="background:rgba(210,153,34,0.08);border-left:4px solid #d29922;padding:12px 16px;border-radius:4px;font-size:0.85em;color:#8b949e;">
⚠️ Le premium ne garantit AUCUN profit. Les signaux sont des outils d'aide à la décision. Toujours DYOR.
</div>
""", unsafe_allow_html=True)
