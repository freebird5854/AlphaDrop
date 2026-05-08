# ALPHA DROP - Product Intelligence Engine PRD

## Original Problem Statement
Build "ALPHA DROP" — The Ultimate Product Intelligence Engine for TikTok Shop. Bloomberg Terminal-style app identifying products BEFORE they go viral using a proprietary AlphaScore algorithm. Full paywall, monetization, creator marketplace.

## COMPLETE FEATURE LIST (All Tested & Passing — 9 iterations, 100%)

### Core Intelligence
- AlphaScore v2.0: 12-factor predictive engine, momentum multiplier, saturation countdown, entry window
- 8 status categories: EXPLOSIVE, SCALING_NOW, EXPLODING_SOON, RISING, EARLY_SIGNAL, SATURATION_WARNING, WATCHLIST, AVOID
- Real-time ticker, Command Bar (Cmd+K), enhanced dashboard with 5 sections
- 271+ real TikTok Shop products via Scrape Creators API

### AI-Powered Tools
- AI Script Generator (GPT-4o): 5 video scripts per product
- Comment Sentiment Analysis (GPT-4o): buyer intent, quality, saturation scores
- Ad Creative Library: 70+ tracked creatives, top hooks, duplication alerts
- Time-Series Forecasting: predict 7/14/30 days, viral probability

### Marketplace & Creators
- TikTok Affiliates: 80+ creators by niche with contact info
- Creator Self-Registration Portal: register, login, profile, browse
- Creator Marketplace (two-sided): sellers post briefs, creators apply
- AI matching engine for product-creator pairing

### Store & Competitor Intelligence
- Shopify Store Tracking: add/remove stores, real /products.json fetch, revenue estimates
- Google Trends integration (pytrends)
- Amazon demand estimation algorithm
- Cross-platform Market Validation

### Platform & Monetization
- Stripe: Scout $79, Hunter $199, Predator $499, Affiliate Pro +$99
- Full paywall with mock data landing page demo
- Google OAuth (users) + JWT admin panel (/admin)
- REST API v1 for Predator (API key auth)
- Team collaboration (3 seats for Predator)
- CSV export, Weekly Winners Report, push notifications
- PWA manifest + Native app (Expo WebView wrapper)
- Privacy Policy (/privacy) & Terms of Service (/terms)
- Historical data tracking (daily snapshots)
- Beta waitlist (25% off founding members)

### Admin
- URL: /admin | Email: admin@alphadrop.com | Password: AlphaDr0p!2026

## Architecture
```
/app/backend/server.py — Main FastAPI (AlphaScore, auth, products, billing)
/app/backend/routes/ — 10 modular routers:
  affiliates, history, api_access, team, trends,
  ai_tools, ad_library, forecast, store_tracking,
  marketplace, creator_portal, push_notifications
/app/frontend/src/ — React + Tailwind + Shadcn + Recharts + cmdk
/app/native-app/ — Expo React Native wrapper
```

## Files
- /app/EXPANSION_PLAN.md — Full 20-week strategic roadmap
- /app/AD_CAMPAIGN_PROMPT.md — LLM prompt for ad campaign generation
- /app/NATIVE_APP_GUIDE.md — Complete App Store submission guide
