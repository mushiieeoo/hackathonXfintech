from fastapi import APIRouter, HTTPException
from models.schemas import InvestmentStrategy
from services.rebalancing_service import (
    save_strategy,
    get_strategy,
    get_rebalancing_advice,
    take_monthly_snapshot,
    get_latest_snapshot,
)

router = APIRouter()


@router.post("/strategy")
async def set_strategy(strategy: InvestmentStrategy):
#Feature 3 — Save the user's target investment strategy
    try:
        strategy.validate_total()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return await save_strategy(strategy)


@router.get("/strategy")
async def fetch_strategy():
#Feature 3 — Retrieve the current investment strategy
    strategy = await get_strategy()
    if not strategy:
        raise HTTPException(status_code=404, detail="No strategy configured yet.")
    return strategy


@router.get("/snapshot/latest")
async def fetch_latest_snapshot():
#Return the most recent monthly ratio snapshot
    snapshot = await get_latest_snapshot()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot available yet.")
    return snapshot


@router.post("/snapshot/manual")
async def trigger_manual_snapshot():
#Manually trigger a portfolio ratio snapshot (for testing)
    snap = await take_monthly_snapshot()
    snap.pop("_id", None)
    return {"message": "Snapshot taken.", "snapshot": snap}


@router.get("/advice")
async def fetch_rebalancing_advice():

    #Feature 3 — Main rebalancing dashboard 

    try:
        return await get_rebalancing_advice()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
