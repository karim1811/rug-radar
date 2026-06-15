import streamlit as st

LOGO = "https://user-gen-media-assets.s3.amazonaws.com/gemini_images/2877ac40-2405-4447-b8a8-4526ddbadd72.png"

st.set_page_config(page_title="Premium Aladin Crypto", page_icon=LOGO, layout="wide")

st.markdown("""
<style>
.stApp { background: #0b1020; }
.header-wrap{display:flex;align-items:center;gap:14px;margin-bottom:1rem;padding:6px 0 10px 0;}
.header-img{width:54px;height:54px;border-radius:16px;object-fit:cover;box-shadow:0 4px 14px rgba(0,0,0,.28);flex-shrink:0;}
.header-title{font-size:2.15rem;font-weight:800;line-height:1.05;color:#fff;}
.card{padding:1rem 1.05rem;border-radius:18px;border:1px solid rgba(255,255,255,.08);background:linear-gradient(180deg, rgba(18,23,38,.96), rgba(10,14,24,.96));box-shadow:0 10px 32px rgba(0,0,0,.18);}
.badge{display:inline-block;padding:.25rem .6rem;border-radius:999px;background:rgba(34,197,94,.14);color:#86efac;font-weight:700;font-size:.82rem;}
.price{font-size:2rem;font-weight:900;margin:.2rem 0 .5rem 0;}
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
    st.markdown("<span class='badge'>OFFRE PREMIUM</span>", unsafe_allow_html=True)
    st.markdown("### Ce que contient le premium")
    st.write("Accès aux signaux avancés, aux alertes privées et au suivi prioritaire des actifs les plus intéressants.")

left, right = st.columns([1.1, 1])
with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Inclus")
    st.markdown("""- Signaux techniques avancés.
- Suivi prioritaire des tokens.
- Mise à jour des opportunités.
- Lecture plus rapide du marché.
- Accès privé après paiement.""")
    st.markdown("### Pour qui")
    st.write("Pour ceux qui veulent aller plus vite que la version gratuite et recevoir des infos plus ciblées.")
    st.markdown("</div>", unsafe_allow_html=True)
with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Tarif")
    st.markdown("<div class='price'>Prix à définir</div>", unsafe_allow_html=True)
    st.write("Tu peux mettre ici ton tarif final quand tu l’auras décidé.")
    st.markdown("### Accès")
    st.link_button("Payer / demander l'accès", "https://ton-lien-de-paiement.com")
    st.write("L’accès au contenu privé est donné après paiement.")
    st.markdown("### Important")
    st.write("Le lien d'accès privé doit être envoyé uniquement aux personnes qui ont payé.")
    st.markdown("</div>", unsafe_allow_html=True)