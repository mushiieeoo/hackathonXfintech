from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ── Asset Input Models ─────────────────────────────────────────────────────────

class BankEntry(BaseModel):
    bank_name: str
    amount_RM: float
    save_date: datetime = Field(default_factory=datetime.utcnow)

class CryptoEntry(BaseModel):
    crypt_name: str       # e.g. "BTC", "ETH"
    coin_amount: float
    date_price: datetime = Field(default_factory=datetime.utcnow)

class ETFEntry(BaseModel):
    etf_name: str         # e.g. "VWRA", "SPY"
    share_amount: float
    date_price: datetime = Field(default_factory=datetime.utcnow)

class StockEntry(BaseModel):
    stock_name: str       # e.g. "AAPL", "TSLA"
    share_amount: float
    date_price: datetime = Field(default_factory=datetime.utcnow)

class NVIEntry(BaseModel):
    nvi_name: str         # e.g. "Fixed Deposit", "Gold"
    amount_RM: float
    save_date: datetime = Field(default_factory=datetime.utcnow)


# ── Settings Models ────────────────────────────────────────────────────────────

class MonthlyPlanUpdate(BaseModel):
    monthly_plan_RM: float

class InvestmentStrategy(BaseModel):
    etf_pct: float        # e.g. 20.0
    stock_pct: float      # e.g. 10.0
    crypto_pct: float     # e.g. 10.0
    nvi_pct: float        # e.g. 60.0

    def validate_total(self):
        total = self.etf_pct + self.stock_pct + self.crypto_pct + self.nvi_pct
        if abs(total - 100.0) > 0.01:
            raise ValueError(f"Strategy percentages must sum to 100, got {total}")


# ── Goal Models ────────────────────────────────────────────────────────────────

class YearlyGoal(BaseModel):
    year: int
    target_RM: float

class GoalMilestone(BaseModel):
    year: int
    target_RM: float
    current_value_RM: float
    progress_pct: float
    milestones_reached: List[int]   # e.g. [30, 50] if those are unlocked
    tree_stage: int                  # 0=seed, 1=sprout, 2=sapling, 3=young, 4=full


# ── Portfolio Response Models ──────────────────────────────────────────────────

class AssetGroupValue(BaseModel):
    label: str
    value_RM: float
    ratio_pct: float

class PortfolioSummary(BaseModel):
    total_value_RM: float
    breakdown: List[AssetGroupValue]
    last_updated: datetime


# ── Rebalancing Models ─────────────────────────────────────────────────────────

class RebalancingSnapshot(BaseModel):
    snapshot_date: datetime
    etf_pct: float
    stock_pct: float
    crypto_pct: float
    nvi_pct: float

class RebalancingAdvice(BaseModel):
    strategy: InvestmentStrategy
    current_snapshot: RebalancingSnapshot
    monthly_plan_RM: float
    drift: dict                      # how far each asset is from target
    ai_advice: str                   # Gemini response
    allocations: dict                # suggested RM amounts per category
