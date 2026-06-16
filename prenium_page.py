import streamlit as st

LOGO = "https://user-gen-media-assets.s3.amazonaws.com/gemini_images/2877ac40-2405-4447-b8a8-4526ddbadd72.png"

st.set_page_config(page_title="RugRadar Premium", page_icon=LOGO, layout="wide")

st.markdown("""
<style>
.stApp { background: #0b1020; }
.header-wrap{display:flex;align-items:center;gap:14px;margin-bottom:1rem;padding:6px 0 10px 0;}
.header-img{width:54px;height:54px;border-radius:16px;object-fit:cover;box-shadow:0 4px 14px rgba(0,0,0,.28);flex-shrink:0;}
.header-title{font-size:2.15rem;font-weight:800;line-height:1.05;color:#fff;}
.card{padding:1rem 1.05rem;border-radius:18px;border:1px solid rgba(255,255,255,.08);background:linear-gradient(180deg, rgba(18,23,38,.96), rgba(10,14,24,.96));box-shadow:0 10px 32px rgba(0,0,0,.18);}
.badge{display:inline-block;padding:.25rem .6rem;border-radius:999px;background:rgba(234,179,8,.15);color:#fbbf24;font-weight:700;font-size:.82rem;}
.price{font-size:2rem;font-weight:900;margin:.2rem 0 .5rem 0;}
.feature{display:flex;align-items:center;gap:8px;padding:6px 0;font-size:.95em;}
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

# ── Plans ──
st.subheader("Nos offres")
p1, p2, p3 = st.columns(3)

with p1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("#### 🆓 Gratuit")
    st.markdown("<div class='price'>0€</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='feature'>✅ Scanner de tokens</div>
    <div class='feature'>✅ Watchlist basique</div>
    <div class='feature'>✅ Données marché</div>
    <div class='feature'>❌ Signaux avancés</div>
    <div class='feature'>❌ Alertes temps réel</div>
    <div class='feature'>❌ Support prioritaire</div>
    """, unsafe_allow_html=True)
    st.button("Plan actuel", disabled=True, use_container_width=True, key="plan_free")
    st.markdown("</div>", unsafe_allow_html=True)

with p2:
    st.markdown("<div class='card' style='border-color:rgba(234,179,8,.3);'>", unsafe_allow_html=True)
    st.markdown("#### ⚡ Pro")
    st.markdown("<div class='price'>9.99€<span style='font-size:.9rem;font-weight:400;color:#8b949e;'>/mois</span></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='feature'>✅ Tout le gratuit</div>
    <div class='feature'>✅ Signaux avancés</div>
    <div class='feature'>✅ Alertes Telegram</div>
    <div class='feature'>✅ Watchlist illimitée</div>
    <div class='feature'>✅ Support prioritaire</div>
    <div class='feature'>❌ API access</div>
    """, unsafe_allow_html=True)
    st.link_button("Choisir Pro", "https://buy.stripe.com/test_placeholder", use_container_width=True, key="plan_pro")
    st.markdown("</div>", unsafe_allow_html=True)

with p3:
    st.markdown("<div class='card' style='border-color:rgba(139,92,246,.3);'>", unsafe_allow_html=True)
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
    st.link_button("Choisir Ultimate", "https://buy.stripe.com/test_placeholder2", use_container_width=True, key="plan_ultimate")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ── FAQ ──
st.subheader("FAQ")
with st.expansion("Comment fonctionne le premium ?"):
    st.write("Après paiement, tu reçois un accès aux fonctionnalités avancées : signaux de trading automatiques, alertes Telegram en temps réel, et une watchlist illimitée.")
with st.expansion("Quels moyens de paiement ?"):
    st.write("Carte bancaire via Stripe. Bientôt PayPal et crypto.")
with st.expansion("Puis-je annuler à tout moment ?"):
    st.write("Oui, pas d'engagement. Tu peux annuler depuis ton espace.")
with st.expansion("C'est quoi les signaux avancés ?"):
    st.write("Des alertes basées sur l'analyse de risque RugRadar + des patterns de manipulation détectés en temps réel. Seulement pour les tokens avec un score de risque bas.")

st.write("")
st.markdown("""
<div style="background:rgba(210,153,34,0.08);border-left:4px solid #d29922;padding:12px 16px;border-radius:4px;font-size:0.85em;color:#8b949e;">
⚠️ Le premium ne garantit AUCUN profit. Les signaux sont des outils d'aide à la décision. Toujours DYOR.
</div>
""", unsafe_allow_html=True)
