from fastapi import APIRouter, HTTPException
from models.schemas import YearlyGoal
from services.goal_service import set_goal, get_goal_milestone
from datetime import datetime

router = APIRouter()


@router.post("", include_in_schema=True)
async def create_or_update_goal(goal: YearlyGoal):
    #Feature 2 — Set a yearly investment goal.
    if goal.target_RM <= 0:
        raise HTTPException(status_code=400, detail="Target must be greater than 0")
    return await set_goal(goal)


@router.get("/{year}")
async def fetch_goal_milestone(year: int):
    #Feature 2 — Get milestone progress and tree stage for a given year.
    try:
        return await get_goal_milestone(year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
async def current_year_goal():
    #Shortcut — returns milestone for the current year.
    year = datetime.utcnow().year
    try:
        return await get_goal_milestone(year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
