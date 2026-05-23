"""
Price service — fetches real-time prices for volatile assets.

Sources:
  - Crypto  : CoinGecko free API (no key required)
  - ETF/Stock: Yahoo Finance via yfinance (no key required)
  - Prices cached in MongoDB price_cache collection
"""

import asyncio
from datetime import datetime
from typing import Optional
import httpx
import yfinance as yf
from database import crypto_col, etf_col, stock_col, price_cache_col


COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# Map common ticker -> CoinGecko id
COINGECKO_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "MATIC": "matic-network",
}

MYR_RATE_SYMBOL = "MYR=X"   # USD→MYR via Yahoo Finance


async def _fetch_usd_to_myr() -> float:
    """Fetch current USD to MYR exchange rate."""
    try:
        loop = asyncio.get_event_loop()
        ticker = await loop.run_in_executor(None, lambda: yf.Ticker(MYR_RATE_SYMBOL))
        info = await loop.run_in_executor(None, lambda: ticker.fast_info)
        rate = getattr(info, "last_price", None)
        if rate and rate > 0:
            return float(rate)
    except Exception:
        pass
    return 4.70   # Fallback rate


async def fetch_crypto_price_myr(symbol: str) -> Optional[float]:
    #Fetch crypto price in MYR via CoinGecko
    cg_id = COINGECKO_ID_MAP.get(symbol.upper(), symbol.lower())
    url = f"{COINGECKO_BASE}/simple/price"
    params = {"ids": cg_id, "vs_currencies": "myr"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            price = data.get(cg_id, {}).get("myr")
            if price:
                return float(price)
    except Exception:
        pass
    return None


async def fetch_equity_price_myr(symbol: str, usd_to_myr: float) -> Optional[float]:
    #Fetch ETF / stock price in MYR via yfinance (prices usually in USD)
    try:
        loop = asyncio.get_event_loop()
        ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol))
        info = await loop.run_in_executor(None, lambda: ticker.fast_info)
        price_usd = getattr(info, "last_price", None)
        currency = getattr(info, "currency", "USD")
        if price_usd is None:
            return None
        if currency == "MYR":
            return float(price_usd)
        return float(price_usd) * usd_to_myr
    except Exception:
        return None


async def cache_price(symbol: str, price_myr: float, asset_type: str):
    #Upsert price into price_cache collection
    await price_cache_col.update_one(
        {"symbol": symbol},
        {
            "$set": {
                "symbol": symbol,
                "price_myr": price_myr,
                "asset_type": asset_type,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )


async def get_cached_price(symbol: str) -> Optional[float]:
    #Return cached price (used as fallback if live fetch fails)
    doc = await price_cache_col.find_one({"symbol": symbol})
    return doc["price_myr"] if doc else None


async def refresh_all_prices():
    """
    Called every minute by the scheduler.
    Fetches prices for all crypto, ETF, and stock symbols in the DB.
    """
    usd_to_myr = await _fetch_usd_to_myr()

    # Gather unique symbols
    crypto_docs = await crypto_col.distinct("crypt_name")
    etf_docs = await etf_col.distinct("etf_name")
    stock_docs = await stock_col.distinct("stock_name")

    tasks = []

    async def update_crypto(sym):
        price = await fetch_crypto_price_myr(sym)
        if price:
            await cache_price(sym, price, "crypto")

    async def update_equity(sym, asset_type):
        price = await fetch_equity_price_myr(sym, usd_to_myr)
        if price:
            await cache_price(sym, price, asset_type)

    for sym in crypto_docs:
        tasks.append(update_crypto(sym))
    for sym in etf_docs:
        tasks.append(update_equity(sym, "etf"))
    for sym in stock_docs:
        tasks.append(update_equity(sym, "stock"))

    await asyncio.gather(*tasks, return_exceptions=True)
