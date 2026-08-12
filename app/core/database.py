from motor.motor_asyncio import AsyncIOMotorClient

# Connection string for a local MongoDB instance
MONGO_URL = "mongodb://localhost:27017"

# Initialize the MongoDB client
client = AsyncIOMotorClient(MONGO_URL)

# Create (or connect to) a database named 'ai_job_portal'
db = client.ai_job_portal

# Define our collections (these act like tables in SQL)
users_collection = db.get_collection("users")
jobs_collection = db.get_collection("jobs")
resumes_collection = db.get_collection("resumes")

print("MongoDB connection established successfully.")