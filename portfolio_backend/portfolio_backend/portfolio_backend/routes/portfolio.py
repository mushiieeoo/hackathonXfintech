from fastapi import APIRouter, HTTPException
from models.schemas import MonthlyPlanUpdate
from services.portfolio_service import compute_portfolio_summary
from services.rebalancing_service import save_monthly_plan, get_monthly_plan

router = APIRouter()


@router.get("/summary")
async def get_portfolio_summary():
    """
    Feature 1 — Returns current portfolio value breakdown for the pie chart.
    Includes total value, per-category values, and ratios.
    """
    summary = await compute_portfolio_summary()
    return summary


@router.get("/monthly-plan")
async def fetch_monthly_plan():
    amount = await get_monthly_plan()
    return {"monthly_plan_RM": amount}


@router.post("/monthly-plan")
async def update_monthly_plan(payload: MonthlyPlanUpdate):
    #Set/update the user's monthly investment plan amount.
    if payload.monthly_plan_RM <= 0:
        raise HTTPException(status_code=400, detail="Monthly plan must be greater than 0")
    return await save_monthly_plan(payload.monthly_plan_RM)
