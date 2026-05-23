# test_connection.py
from dotenv import load_dotenv
import os

load_dotenv()
print("mongo_uri =", os.getenv("mongo_uri"))