from datetime import datetime
from typing import Dict
from database import bank_col, crypto_col, etf_col, stock_col, nvi_col, price_cache_col
from models.schemas import AssetGroupValue, PortfolioSummary


async def _get_price(symbol: str) -> float:
    doc = await price_cache_col.find_one({"symbol": symbol})
    return doc["price_myr"] if doc else 0.0


async def compute_portfolio_summary() -> PortfolioSummary:

    # ETF
    etf_total = 0.0
    async for doc in etf_col.find():
        price = await _get_price(doc["etf_name"])
        etf_total += doc["share_amount"] * price

    # Stock
    stock_total = 0.0
    async for doc in stock_col.find():
        price = await _get_price(doc["stock_name"])
        stock_total += doc["share_amount"] * price

    # Crypto
    crypto_total = 0.0
    async for doc in crypto_col.find():
        price = await _get_price(doc["crypt_name"])
        crypto_total += doc["coin_amount"] * price

    # Non-Volatile (Bank + NVI)
    nvi_total = 0.0
    async for doc in nvi_col.find():
        nvi_total += doc["amount_RM"]
    async for doc in bank_col.find():
        nvi_total += doc["amount_RM"]

    grand_total = etf_total + stock_total + crypto_total + nvi_total

    def ratio(val: float) -> float:
        return round((val / grand_total * 100), 2) if grand_total > 0 else 0.0

    breakdown = [
        AssetGroupValue(label="ETF",             value_RM=round(etf_total, 2),    ratio_pct=ratio(etf_total)),
        AssetGroupValue(label="Stock",           value_RM=round(stock_total, 2),  ratio_pct=ratio(stock_total)),
        AssetGroupValue(label="Crypto",          value_RM=round(crypto_total, 2), ratio_pct=ratio(crypto_total)),
        AssetGroupValue(label="Non-Volatile",    value_RM=round(nvi_total, 2),    ratio_pct=ratio(nvi_total)),
    ]

    return PortfolioSummary(
        total_value_RM=round(grand_total, 2),
        breakdown=breakdown,
        last_updated=datetime.utcnow(),
    )


async def get_current_ratios() -> Dict[str, float]:
    #Return current ratios as a plain dict (used by rebalancing service).
    summary = await compute_portfolio_summary()
    return {item.label: item.ratio_pct for item in summary.breakdown}
