from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from dotenv import load_dotenv
import os
load_dotenv()

MONGO_URI = os.getenv("mongo_uri", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "portfoAI")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections matching capital.py schema
bank_col = db["bank_data"]          # bank_name, amount_RM, save_date
crypto_col = db["crypt_data"]      # crypt_name, coin_amount, date_price
etf_col = db["etf_data"]            # etf_name, share_amount, date_price
stock_col = db["stock_data"]        # stock_name, share_amount, date_price
nvi_col = db["nvi_data"]            # nvi_name, amount_RM, save_date

# App-level collections
settings_col = db["settings"]           # monthly_plan, investment_strategy
goals_col = db["goals"]                 # yearly goals
rebalancing_col = db["rebalancing_snapshots"]  # monthly ratio snapshots
price_cache_col = db["price_cache"]     # latest fetched prices


async def init_indexes():
#index for performances
    await crypto_col.create_index([("crypt_name", ASCENDING)])
    await etf_col.create_index([("etf_name", ASCENDING)])
    await stock_col.create_index([("stock_name", ASCENDING)])
    await price_cache_col.create_index([("symbol", ASCENDING)], unique=True)
    await rebalancing_col.create_index([("snapshot_date", ASCENDING)])
