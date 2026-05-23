from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
client = AsyncIOMotorClient(os.getenv("mongo_uri"))
db = client["portfoAI"]

async def seed():
    # Bank
    await db["bank_data"].insert_many([
        {"bank_name": "Maybank", "amount_RM": 1000, "save_date": "2026-02-25"},
        {"bank_name": "CIMB", "amount_RM": 500, "save_date": "2026-02-25"}
    ])

    # Crypto
    await db["crypto_data"].insert_many([
        {"crypt_name": "BTC", "coin_amount": 0.005, "date_price": "2026-01-20"},
        {"crypt_name": "ETH", "coin_amount": 0.5777, "date_price": "2026-01-10"}
    ])

    # ETF
    await db["etf_data"].insert_many([
        {"etf_name": "VWRA", "share_amount": 100, "date_price": "2026-02-11"},
        {"etf_name": "SPY", "share_amount": 70, "date_price": "2026-01-21"}
    ])

    # Stock
    await db["stock_data"].insert_many([
        {"stock_name": "NVDA", "share_amount": 1000, "date_price": "2026-01-09"},
        {"stock_name": "MAYBANK.KL", "share_amount": 1500, "date_price": "2026-02-04"}
    ])

    # NVI
    await db["nvi_data"].insert_many([
        {"nvi_name": "ASB", "amount_RM": 10000, "save_date": "2026-01-01"},
        {"nvi_name": "Physical Gold", "amount_RM": 3000, "save_date": "2026-03-01"}
    ])

    print("Data seeded successfully!")

asyncio.run(seed())