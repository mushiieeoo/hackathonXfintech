from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routes import portfolio, goals, rebalancing, assets
from database import init_indexes
from services.scheduler_service import (
    update_prices_job,
    monthly_rebalancing_snapshot_job,
)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_indexes()
    # Every minute: refresh volatile asset prices
    scheduler.add_job(update_prices_job, "interval", minutes=1, id="price_update")
    # 1st of every month at 00:05: snapshot ratios for rebalancing
    scheduler.add_job(
        monthly_rebalancing_snapshot_job,
        "cron",
        day=1,
        hour=0,
        minute=5,
        id="monthly_snapshot",
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Portfolio Tracker API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(rebalancing.router, prefix="/api/rebalancing", tags=["Rebalancing"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])


@app.get("/")
def root():
    return {"status": "Portfolio Tracker API is running"}
