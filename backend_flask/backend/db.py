from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the database connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/portfoTrack_db")
client = MongoClient(MONGO_URI)

# This 'db' variable is what we will import into our routes!
db = client.get_database()