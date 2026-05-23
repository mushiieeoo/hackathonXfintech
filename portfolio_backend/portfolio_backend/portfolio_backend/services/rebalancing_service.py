#compares current ratios vs strategy and calls Gemini for advice.

import asyncio
import os
from datetime import datetime
from typing import Optional
import httpx
from database import settings_col, rebalancing_col
from models.schemas import InvestmentStrategy, RebalancingSnapshot, RebalancingAdvice
from services.portfolio_service import get_current_ratios

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


# CRUD

async def save_strategy(strategy: InvestmentStrategy) -> dict:
    strategy.validate_total()
    await settings_col.update_one(
        {"_type": "strategy"},
        {"$set": {
            "_type": "strategy",
            "etf_pct": strategy.etf_pct,
            "stock_pct": strategy.stock_pct,
            "crypto_pct": strategy.crypto_pct,
            "nvi_pct": strategy.nvi_pct,
            "updated_at": datetime.utcnow(),
        }},
        upsert=True,
    )
    return {"message": "Investment strategy saved."}


async def get_strategy() -> Optional[InvestmentStrategy]:
    doc = await settings_col.find_one({"_type": "strategy"})
    if not doc:
        return None
    return InvestmentStrategy(
        etf_pct=doc["etf_pct"],
        stock_pct=doc["stock_pct"],
        crypto_pct=doc["crypto_pct"],
        nvi_pct=doc["nvi_pct"],
    )


#monthly plan

async def save_monthly_plan(amount_rm: float) -> dict:
    await settings_col.update_one(
        {"_type": "monthly_plan"},
        {"$set": {"_type": "monthly_plan", "amount_RM": amount_rm, "updated_at": datetime.utcnow()}},
        upsert=True,
    )
    return {"message": f"Monthly plan set to RM {amount_rm}"}


async def get_monthly_plan() -> float:
    doc = await settings_col.find_one({"_type": "monthly_plan"})
    return doc["amount_RM"] if doc else 0.0


#snapshot

async def take_monthly_snapshot():
    #Store current ratios as a rebalancing snapshot
    ratios = await get_current_ratios()
    snapshot = {
        "snapshot_date": datetime.utcnow(),
        "etf_pct": ratios.get("ETF", 0.0),
        "stock_pct": ratios.get("Stock", 0.0),
        "crypto_pct": ratios.get("Crypto", 0.0),
        "nvi_pct": ratios.get("Non-Volatile", 0.0),
    }
    await rebalancing_col.insert_one(snapshot)
    return snapshot


async def get_latest_snapshot() -> Optional[RebalancingSnapshot]:
    doc = await rebalancing_col.find_one(sort=[("snapshot_date", -1)])
    if not doc:
        return None
    return RebalancingSnapshot(
        snapshot_date=doc["snapshot_date"],
        etf_pct=doc["etf_pct"],
        stock_pct=doc["stock_pct"],
        crypto_pct=doc["crypto_pct"],
        nvi_pct=doc["nvi_pct"],
    )


#Gemini AI Advice
def _build_gemini_prompt(
    strategy: InvestmentStrategy,
    snapshot: RebalancingSnapshot,
    monthly_plan_rm: float,
    drift: dict,
) -> str:
    return f"""You are a personal investment advisor. 
A user has a monthly investment budget of RM {monthly_plan_rm:.2f}.

Their TARGET investment strategy is:
- ETF: {strategy.etf_pct}%
- Stock: {strategy.stock_pct}%
- Crypto: {strategy.crypto_pct}%
- Non-Volatile Assets (e.g. fixed deposit, savings): {strategy.nvi_pct}%

At the start of this month (snapshot), their portfolio ratio was:
- ETF: {snapshot.etf_pct:.2f}%
- Stock: {snapshot.stock_pct:.2f}%
- Crypto: {snapshot.crypto_pct:.2f}%
- Non-Volatile Assets: {snapshot.nvi_pct:.2f}%

The drift from target (positive = over-allocated, negative = under-allocated):
- ETF: {drift['etf']:.2f}%
- Stock: {drift['stock']:.2f}%
- Crypto: {drift['crypto']:.2f}%
- Non-Volatile: {drift['nvi']:.2f}%

Based on this drift, advise the user specifically how to allocate their RM {monthly_plan_rm:.2f} this month 
across ETF, Stock, Crypto, and Non-Volatile Assets to bring their portfolio closer to their target strategy.
Give concrete RM amounts for each category. Be concise (3–5 sentences), practical, and friendly.
Do not suggest selling assets."""


async def _call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "Gemini API key not configured. Please set GEMINI_API_KEY in your environment."
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 512},
    }
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.post(url, json=payload, headers=headers)
                if r.status_code == 429:
                    await asyncio.sleep((attempt + 1) * 5)
                    continue
                r.raise_for_status()
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            if attempt == 2:
                return "AI advice temporarily unavailable — your allocation suggestions above are still accurate!"
    return "AI advice temporarily unavailable — your allocation suggestions above are still accurate!"


def _suggest_allocations(
    strategy: InvestmentStrategy,
    drift: dict,
    monthly_plan_rm: float,
) -> dict:
    """
    Simple rule: allocate more to under-weight categories.
    Under-weight = negative drift (current < target).
    """
    under = {
        "ETF": max(0.0, -drift["etf"]),
        "Stock": max(0.0, -drift["stock"]),
        "Crypto": max(0.0, -drift["crypto"]),
        "Non-Volatile": max(0.0, -drift["nvi"]),
    }
    total_under = sum(under.values())

    if total_under == 0:
        # Portfolio is balanced — allocate by strategy
        return {
            "ETF": round(monthly_plan_rm * strategy.etf_pct / 100, 2),
            "Stock": round(monthly_plan_rm * strategy.stock_pct / 100, 2),
            "Crypto": round(monthly_plan_rm * strategy.crypto_pct / 100, 2),
            "Non-Volatile": round(monthly_plan_rm * strategy.nvi_pct / 100, 2),
        }

    return {
        k: round(monthly_plan_rm * v / total_under, 2) for k, v in under.items()
    }


async def get_rebalancing_advice() -> RebalancingAdvice:
    strategy = await get_strategy()
    if not strategy:
        raise ValueError("No investment strategy set. Please configure your strategy first.")

    snapshot = await get_latest_snapshot()
    if not snapshot:
        # Take a live snapshot on-demand if none exists
        raw = await take_monthly_snapshot()
        raw.pop("_id",None)
        snapshot = RebalancingSnapshot(**raw)

    monthly_plan = await get_monthly_plan()

    drift = {
        "etf":   round(snapshot.etf_pct - strategy.etf_pct, 2),
        "stock": round(snapshot.stock_pct - strategy.stock_pct, 2),
        "crypto": round(snapshot.crypto_pct - strategy.crypto_pct, 2),
        "nvi":   round(snapshot.nvi_pct - strategy.nvi_pct, 2),
    }

    prompt = _build_gemini_prompt(strategy, snapshot, monthly_plan, drift)
    ai_advice = await _call_gemini(prompt)
    allocations = _suggest_allocations(strategy, drift, monthly_plan)

    return RebalancingAdvice(
        strategy=strategy,
        current_snapshot=snapshot,
        monthly_plan_RM=monthly_plan,
        drift=drift,
        ai_advice=ai_advice,
        allocations=allocations,
    )
