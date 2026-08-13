from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from app.api import auth, resumes  
from app.api import companies, jobs, match, admin  
from bson import ObjectId
from fastapi.staticfiles import StaticFiles
from app.core.database import db  # <-- Motor (async) database, shared across the app
import shutil
import os

app = FastAPI(
    title="AI Job Portal API",
    description="Backend for the AI-powered Job Portal and Resume Analyzer",
    version="1.0.0"
)

# Create a folder to store uploaded images
os.makedirs("uploads", exist_ok=True)

# Tell FastAPI to make this folder publicly readable so Streamlit can display the images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==========================================
# HR: UPLOAD A NEW SOCIAL POST
# ==========================================
@app.get("/posts/")
async def get_all_posts():
    try:
        # Check if posts collection exists/has documents safely
        collection_names = await db.list_collection_names()
        if "posts" not in collection_names:
            return []
            
        cursor = db.posts.find().sort("_id", -1)
        posts = await cursor.to_list(length=None)
        
        for post in posts:
            post["id"] = str(post["_id"])
            del post["_id"]
            
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# JOB SEEKER: LIKE A SOCIAL POST
# ==========================================
@app.post("/posts/{post_id}/like")
async def like_post(post_id: str):
    try:
        result = await db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"likes": 1}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"message": "Liked successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# ADMIN: FETCH PENDING COMPANIES
# ==========================================
@app.get("/companies/pending")
async def get_pending_companies(): 
    try:
        cursor = db.companies.find({"is_verified": {"$ne": True}})
        pending_companies = await cursor.to_list(length=None)
        
        for comp in pending_companies:
            comp["id"] = str(comp["_id"])
            del comp["_id"]
            
        return pending_companies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ==========================================
# ROUTER REGISTRATION
# ==========================================
# <-- ALL INCLUDES MUST STAY AT THE BOTTOM
app.include_router(companies.router)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"]) 
app.include_router(jobs.router)
app.include_router(match.router)
app.include_router(admin.router, prefix="/admin", tags=["Admin"]) 

# ==========================================
# ADMIN: FETCH PLATFORM STATISTICS
# ==========================================
@app.get("/admin/stats")
async def get_platform_stats():
    try:
        # Count documents in the database collections
        total_users = await db.users.count_documents({})
        active_jobs = await db.jobs.count_documents({})
        
        return {
            "total_users": total_users,
            "active_job_posts": active_jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Job Portal API. System is online!"}
