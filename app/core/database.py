import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL environment variable is not configured")

if not MONGO_URL.startswith(("mongodb://", "mongodb+srv://")):
    raise RuntimeError(
        "Invalid MONGO_URL format. It must start with mongodb:// or mongodb+srv://"
    )

client = AsyncIOMotorClient(MONGO_URL)
db = client.ai_job_portal

users_collection = db.get_collection("users")
jobs_collection = db.get_collection("jobs")
resumes_collection = db.get_collection("resumes")

print("MongoDB connection established successfully.")
