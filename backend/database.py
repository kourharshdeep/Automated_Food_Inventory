import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
db = client["freshtrack_db"]

# Collections
users_collection = db["users"]
food_items_collection = db["food_items"]
predictions_collection = db["predictions"]
feedback_collection = db["feedback"]
