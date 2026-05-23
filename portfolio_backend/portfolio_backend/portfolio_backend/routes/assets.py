from fastapi import APIRouter, HTTPException
from datetime import datetime
from database import bank_col, crypto_col, etf_col, stock_col, nvi_col, price_cache_col
from models.schemas import BankEntry, CryptoEntry, ETFEntry, StockEntry, NVIEntry

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


# Bank

@router.get("/bank")
async def list_bank():
    return [_serialize(d) async for d in bank_col.find()]

@router.post("/bank")
async def add_bank(entry: BankEntry):
    result = await bank_col.insert_one(entry.model_dump())
    return {"inserted_id": str(result.inserted_id)}

@router.delete("/bank/{bank_name}")
async def delete_bank(bank_name: str):
    r = await bank_col.delete_many({"bank_name": bank_name})
    return {"deleted": r.deleted_count}


# Crypto

@router.get("/crypto")
async def list_crypto():
    docs = [_serialize(d) async for d in crypto_col.find()]
    # Enrich with current cached price
    for d in docs:
        cache = await price_cache_col.find_one({"symbol": d["crypt_name"]})
        d["current_price_myr"] = cache["price_myr"] if cache else None
    return docs

@router.post("/crypto")
async def add_crypto(entry: CryptoEntry):
    result = await crypto_col.insert_one(entry.model_dump())
    return {"inserted_id": str(result.inserted_id)}

@router.delete("/crypto/{crypt_name}")
async def delete_crypto(crypt_name: str):
    r = await crypto_col.delete_many({"crypt_name": crypt_name})
    return {"deleted": r.deleted_count}


# ETF

@router.get("/etf")
async def list_etf():
    docs = [_serialize(d) async for d in etf_col.find()]
    for d in docs:
        cache = await price_cache_col.find_one({"symbol": d["etf_name"]})
        d["current_price_myr"] = cache["price_myr"] if cache else None
    return docs

@router.post("/etf")
async def add_etf(entry: ETFEntry):
    result = await etf_col.insert_one(entry.model_dump())
    return {"inserted_id": str(result.inserted_id)}

@router.delete("/etf/{etf_name}")
async def delete_etf(etf_name: str):
    r = await etf_col.delete_many({"etf_name": etf_name})
    return {"deleted": r.deleted_count}


# Stock

@router.get("/stock")
async def list_stock():
    docs = [_serialize(d) async for d in stock_col.find()]
    for d in docs:
        cache = await price_cache_col.find_one({"symbol": d["stock_name"]})
        d["current_price_myr"] = cache["price_myr"] if cache else None
    return docs

@router.post("/stock")
async def add_stock(entry: StockEntry):
    result = await stock_col.insert_one(entry.model_dump())
    return {"inserted_id": str(result.inserted_id)}

@router.delete("/stock/{stock_name}")
async def delete_stock(stock_name: str):
    r = await stock_col.delete_many({"stock_name": stock_name})
    return {"deleted": r.deleted_count}


# NVI (Non-Volatile)

@router.get("/nvi")
async def list_nvi():
    return [_serialize(d) async for d in nvi_col.find()]

@router.post("/nvi")
async def add_nvi(entry: NVIEntry):
    result = await nvi_col.insert_one(entry.model_dump())
    return {"inserted_id": str(result.inserted_id)}

@router.delete("/nvi/{nvi_name}")
async def delete_nvi(nvi_name: str):
    r = await nvi_col.delete_many({"nvi_name": nvi_name})
    return {"deleted": r.deleted_count}
