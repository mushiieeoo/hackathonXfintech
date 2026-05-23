#Scheduler jobs wired into APScheduler in main.py lifespan.

from services.price_service import refresh_all_prices
from services.rebalancing_service import take_monthly_snapshot

async def update_prices_job():
    #Runs every minute — refresh all volatile asset prices
    try:
        await refresh_all_prices()
        print(f"[Scheduler] Prices refreshed.")
    except Exception as e:
        print(f"[Scheduler] Price refresh error: {e}")

async def monthly_rebalancing_snapshot_job():
    #Runs 1st of each month — snapshot current ratios for rebalancing
    try:
        await take_monthly_snapshot()
        print("[Scheduler] Monthly rebalancing snapshot taken.")
    except Exception as e:
        print(f"[Scheduler] Snapshot error: {e}")
