# 🔍 RugRadar — Crypto Manipulation Detector

RugRadar est une application Streamlit qui analyse les tokens crypto en temps réel pour détecter les signaux de manipulation (rug pull, pump & dump, etc.).

## Fonctionnalités

- **🔍 Scanner** — Recherche n'importe quel token par nom ou adresse de contrat. Analyse de risque 0-100 avec DexScreener.
- **📋 Watchlist** — Ajoute tes tokens et suis-les en temps réel. Ajout/suppression facile.
- **📈 Tokens** — Top 50 coins du marché via CoinGecko avec sparklines 7 jours.
- **🚨 Signaux** — Signaux ACHAT/VENTE/ATTENTE basés sur les trending + risk scoring.
- **📊 Dashboard** — Vue d'ensemble : Fear & Grend, Trending, Top marché.
- **⭐ Premium** — Page d'offres (Pro 9.99€/mois, Ultimate 24.99€/mois).

## APIs utilisées (gratuites, pas de clé requise)

- [DexScreener](https://dexscreener.com/) — Données de pairs DEX en temps réel
- [CoinGecko](https://www.coingecko.com/) — Données de marché globales
- [Alternative.me Fear & Greed](https://alternative.me/crypto/fear-and-greed-index/) — Indice de peur/gourmandise

## Installation

```bash
cd "C:\Users\karim\Desktop\projet crypto"
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install streamlit pandas plotly requests
```

## Lancement

```bash
.venv\Scripts\activate
streamlit run main.py
```

L'app ouvre automatiquement dans ton navigateur sur `http://localhost:8501`.

## Structure

```
projet crypto/
├── main.py                  # Page d'accueil + marché live
├── prenium_page.py          # Page premium / offres
├── requirements.txt         # Dépendances
├── .env                     # Variables d'environnement (API keys optionnelles)
├── services/                # Modules API réutilisables
│   ├── coingecko_service.py
│   ├── binance_service.py
│   ├── helius_service.py
│   └── market_data.py
├── pages/                   # Pages Streamlit
│   ├── rugradar_page.py     # Scanner principal
│   ├── watchlist_page.py    # Watchlist personnalisable
│   ├── token_pages.py       # Top coins
│   ├── signals_pages.py     # Signaux trading
│   └── dashboard.py         # Dashboard
├── assets/                  # Images, logos
├── tests/                   # Tests
└── doc et notes/            # Documentation
```

## Roadmap

- [ ] Intégration Stripe pour le premium
- [ ] Alertes Telegram bot
- [ ] Analyse on-chain via Helius (top holders, liquidity lock)
- [ ] Export watchlist en CSV
- [ ] Mode portefeuille (track P&L)
- [ ] Notifications push navigateur

## Disclaimer

RugRadar est un outil d'analyse, PAS un conseil financier. Toujours DYOR (Do Your Own Research). Les crypto-monnaies comportent un risque de perte totale.
