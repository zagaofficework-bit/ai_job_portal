from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from app.api import auth, resumes  
from app.api import companies, jobs, match, admin  
from bson import ObjectId
from fastapi.staticfiles import StaticFiles
from app.core.database import db  # <-- FIXED: import the working db from database.py instead of creating a broken second client
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
def get_all_posts():
    try:
        # Check if posts collection exists/has documents safely
        if "posts" not in db.list_collection_names():
            return []
            
        cursor = db.posts.find().sort("_id", -1)
        posts = list(cursor)
        
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
def like_post(post_id: str):
    try:
        result = db.posts.update_one(
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
def get_pending_companies(): 
    try:
        cursor = db.companies.find({"is_verified": {"$ne": True}})
        pending_companies = list(cursor) 
        
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
def get_platform_stats():
    try:
        # Count documents in the database collections
        total_users = db.users.count_documents({})
        active_jobs = db.jobs.count_documents({})
        
        return {
            "total_users": total_users,
            "active_job_posts": active_jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Job Portal API. System is online!"}
