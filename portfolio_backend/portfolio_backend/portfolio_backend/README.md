# Portfolio Tracker — Python Backend

FastAPI + MongoDB backend for the Portfolio Tracker web app.

---

## Setup

```bash
cd portfolio_backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           
uvicorn main:app --reload --port 8000
```

Swagger docs: http://localhost:8000/docs

---

## Architecture

```
portfolio_backend/
├── main.py                    # FastAPI app + APScheduler lifespan
├── database.py                # Motor (async MongoDB) client & collections
├── requirements.txt
├── .env.example
├── models/
│   └── schemas.py             # Pydantic models for all request/response types
├── routes/
│   ├── assets.py              # CRUD for all 5 asset types
│   ├── portfolio.py           # Feature 1: pie chart summary
│   ├── goals.py               # Feature 2: milestone tree
│   └── rebalancing.py         # Feature 3: strategy + AI advice
├── services/
│   ├── price_service.py       # Real-time prices (CoinGecko + yfinance)
│   ├── portfolio_service.py   # Aggregate values & ratios
│   ├── goal_service.py        # Tree stage computation
│   ├── rebalancing_service.py # Drift calc + Gemini API call
│   └── scheduler_service.py   # APScheduler job wrappers
```

---

## API Reference

### Assets (CRUD for all 5 types)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assets/bank` | List bank entries |
| POST | `/api/assets/bank` | Add bank entry `{bank_name, amount_RM}` |
| DELETE | `/api/assets/bank/{bank_name}` | Remove bank entries |
| GET | `/api/assets/crypto` | List crypto (with live price) |
| POST | `/api/assets/crypto` | Add crypto `{crypt_name, coin_amount}` |
| DELETE | `/api/assets/crypto/{crypt_name}` | Remove crypto |
| GET | `/api/assets/etf` | List ETF (with live price) |
| POST | `/api/assets/etf` | Add ETF `{etf_name, share_amount}` |
| DELETE | `/api/assets/etf/{etf_name}` | Remove ETF |
| GET | `/api/assets/stock` | List stocks (with live price) |
| POST | `/api/assets/stock` | Add stock `{stock_name, share_amount}` |
| DELETE | `/api/assets/stock/{stock_name}` | Remove stock |
| GET | `/api/assets/nvi` | List non-volatile assets |
| POST | `/api/assets/nvi` | Add NVI `{nvi_name, amount_RM}` |
| DELETE | `/api/assets/nvi/{nvi_name}` | Remove NVI |

---

### Feature 1 — Portfolio Pie Chart

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolio/summary` | Total value + breakdown by category (ETF/Stock/Crypto/NVI) with ratios |
| GET | `/api/portfolio/monthly-plan` | Get current monthly plan amount |
| POST | `/api/portfolio/monthly-plan` | Set monthly plan `{monthly_plan_RM: 2000}` |

**Sample response `/api/portfolio/summary`:**
```json
{
  "total_value_RM": 52300.00,
  "breakdown": [
    {"label": "ETF",          "value_RM": 10460.00, "ratio_pct": 20.0},
    {"label": "Stock",        "value_RM": 5230.00,  "ratio_pct": 10.0},
    {"label": "Crypto",       "value_RM": 5230.00,  "ratio_pct": 10.0},
    {"label": "Non-Volatile", "value_RM": 31380.00, "ratio_pct": 60.0}
  ],
  "last_updated": "2025-01-15T08:30:00Z"
}
```

---

### Feature 2 — Goal Milestone Tree

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/goals/` | Set yearly goal `{year: 2025, target_RM: 100000}` |
| GET | `/api/goals/` | Milestone for current year |
| GET | `/api/goals/{year}` | Milestone for specific year |

**Tree stages:** 0=Seed, 1=Sprout (30%), 2=Sapling (50%), 3=Young Tree (70%), 4=Full Tree (100%)

**Sample response:**
```json
{
  "year": 2025,
  "target_RM": 100000,
  "current_value_RM": 52300,
  "progress_pct": 52.3,
  "milestones_reached": [30, 50],
  "tree_stage": 2
}
```

---

### Feature 3 — Strategy Rebalancing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rebalancing/strategy` | Save investment strategy `{etf_pct, stock_pct, crypto_pct, nvi_pct}` (must sum to 100) |
| GET | `/api/rebalancing/strategy` | Get saved strategy |
| GET | `/api/rebalancing/snapshot/latest` | Latest monthly ratio snapshot |
| POST | `/api/rebalancing/snapshot/manual` | Manually trigger a snapshot (testing) |
| GET | `/api/rebalancing/advice` | **Main dashboard** — AI advice + suggested allocations |

**Sample response `/api/rebalancing/advice`:**
```json
{
  "strategy": {"etf_pct": 20, "stock_pct": 10, "crypto_pct": 10, "nvi_pct": 60},
  "current_snapshot": {"etf_pct": 25, "stock_pct": 8, "crypto_pct": 12, "nvi_pct": 55},
  "monthly_plan_RM": 2000,
  "drift": {"etf": 5.0, "stock": -2.0, "crypto": 2.0, "nvi": -5.0},
  "ai_advice": "This month, focus your RM 2,000 on Non-Volatile assets and Stocks...",
  "allocations": {"ETF": 0, "Stock": 400, "Crypto": 0, "Non-Volatile": 1600}
}
```

---

## Scheduled Jobs

| Job | Frequency | Action |
|-----|-----------|--------|
| Price refresh | Every 1 min | Fetches live prices for all crypto/ETF/stock via CoinGecko + yfinance |
| Monthly snapshot | 1st of month, 00:05 | Saves current portfolio ratios for rebalancing comparison |

---

## Price Sources

- **Crypto**: CoinGecko free API (no API key needed)
- **ETF / Stocks**: Yahoo Finance via `yfinance` (no API key needed)
- **Currency**: USD→MYR via Yahoo Finance `MYR=X`
- **AI Advice**: Google Gemini 1.5 Flash (requires `GEMINI_API_KEY`)
