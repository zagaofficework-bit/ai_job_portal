from fastapi import APIRouter, Body, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from app.schemas.job import JobCreate, JobResponse
from app.core.database import db
from typing import List, Optional

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

@router.post("/", response_description="Add new job posting", response_model=JobResponse)
async def create_job(job: JobCreate = Body(...)):
    # Convert Pydantic model to a dictionary 
    job_dict = jsonable_encoder(job)
    
    # Insert into the 'jobs' collection
    new_job = await db["jobs"].insert_one(job_dict)
    
    # Retrieve the inserted document 
    created_job = await db["jobs"].find_one({"_id": new_job.inserted_id})
    
    # Convert MongoDB Object ID to a string for the response
    created_job["id"] = str(created_job["_id"])
    
    return created_job


@router.get("/search")
async def search_jobs(
    role: Optional[str] = None,
    experience: Optional[int] = None,
    min_salary: Optional[int] = None,
    lon: Optional[float] = None,
    lat: Optional[float] = None,
    max_distance_km: int = 15
):
    """
    Dynamically fetches jobs based on seeker's experience, location, and salary requirements.
    """
    query = {}

    # 1. Role Match (Uses regex so "Backend" matches "Backend Developer")
    if role:
        query["role"] = {"$regex": role, "$options": "i"}

    # 2. Experience Match (Job requires <= candidate's experience)
    if experience is not None:
        query["required_experience"] = {"$lte": experience}

    # 3. Salary Match (Job offers >= candidate's minimum ask)
    if min_salary is not None:
        query["salary_offered"] = {"$gte": min_salary}

    # 4. Location Match (Geospatial $near query)
    if lat is not None and lon is not None:
        query["location"] = {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat] 
                },
                "$maxDistance": max_distance_km * 1000 # MongoDB expects meters
            }
        }

    try:
        # Execute the query using Motor
        cursor = db.jobs.find(query)
        jobs = await cursor.to_list(length=50) # Limit to 50 results for performance

        # Convert MongoDB ObjectIds to strings so FastAPI can return them as JSON
        for job in jobs:
            job["_id"] = str(job["_id"])

        return {"status": "success", "total_found": len(jobs), "jobs": jobs}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/", response_description="List all jobs", response_model=List[JobResponse])
async def list_jobs():
    # Fetch up to 100 jobs from the database
    jobs = await db["jobs"].find().to_list(100)
    
    # Convert the MongoDB Object IDs to strings for Pydantic
    for job in jobs:
        job["id"] = str(job["_id"])
        
    return jobs