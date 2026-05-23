#Goal service — tracks yearly investment goals and maps progress to tree stages.

from datetime import datetime
from database import goals_col
from models.schemas import YearlyGoal, GoalMilestone
from services.portfolio_service import compute_portfolio_summary

MILESTONES = [30, 50, 70, 100]

def _tree_stage(progress_pct: float) -> int:
    if progress_pct >= 100:
        return 4
    elif progress_pct >= 70:
        return 3
    elif progress_pct >= 50:
        return 2
    elif progress_pct >= 30:
        return 1
    return 0


async def set_goal(goal: YearlyGoal) -> dict:
    await goals_col.update_one(
        {"year": goal.year},
        {"$set": {"year": goal.year, "target_RM": goal.target_RM, "updated_at": datetime.utcnow()}},
        upsert=True,
    )
    return {"message": f"Goal for {goal.year} set to RM {goal.target_RM}"}


async def get_goal_milestone(year: int) -> GoalMilestone:
    #Compute current milestone status for the given year
    goal_doc = await goals_col.find_one({"year": year})
    if not goal_doc:
        raise ValueError(f"No goal set for year {year}")

    target = goal_doc["target_RM"]
    summary = await compute_portfolio_summary()
    current = summary.total_value_RM

    progress_pct = round((current / target * 100), 2) if target > 0 else 0.0
    milestones_reached = [m for m in MILESTONES if progress_pct >= m]
    stage = _tree_stage(progress_pct)

    return GoalMilestone(
        year=year,
        target_RM=target,
        current_value_RM=current,
        progress_pct=progress_pct,
        milestones_reached=milestones_reached,
        tree_stage=stage,
    )
