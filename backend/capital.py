from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
#print(os.getenv("mongo_uri"))
client=MongoClient(os.getenv("mongo_uri"))
db=client["portfoAI"]

#data collections
bank_data=db["bank_data"]
crypto_data=db["crypt_data"]
etf_data=db["etf_data"]
stock_data=db["stock_data"]
nvi_data=db["nvi_data"]

#bank data
bank_data.insert_many([
    {"bank_type":"Maybank","amount_RM":1000,"save_date":"2026-2-25"},
    {"bank_type":"RHB","amount_RM":2500,"save_date":"2026-2-05"}
])

#crypto data
crypto_data.insert_many([
    {"crypt_name":"Ethereum","coin_amount":0.5777,"date_price":"2026-01-10"},
    {"crypt_name":"Bitcoin","coin_amount":0.005,"date_price":"2026-01-20"}
])

#etf data
etf_data.insert_many([
    {"etf_name":"MyETF Shariah","share_amount":100,"date_price":"2026-02-11"},
    {"etf_name":"KLCI ETF", "share_amount":70,"date_price":"2026-01-21"}
])

#stock data
stock_data.insert_many([
    {"stock_name":"NVIDIA Corp.","share_amount":1000,"date_price":"2026-01-9"},
    {"stock_name":"Maybank","share_amount":1500,"date_price":"2026-02-04"}
])

#nonvolatile investment data
nvi_data.insert_many([
    {"nvi_name":"ASB","amount_RM":4050,"save_data":"2026-01-16"},
    {"nvi_name":"Gold","amount_RM":5500,"save_data":"2026-1-30"}
])

#print("Test:All data successfully added")