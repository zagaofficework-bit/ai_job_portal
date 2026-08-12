from fastapi import APIRouter, HTTPException, Body
from app.core.database import db
from pydantic import BaseModel
from bson import ObjectId
import spacy

# Load the English NLP model
# Note: You must have run `python -m spacy download en_core_web_sm` in your terminal
nlp = spacy.load("en_core_web_sm")

router = APIRouter(
    prefix="/match",
    tags=["AI Matching"]
)

# Create a Pydantic model for our incoming request
class MatchRequest(BaseModel):
    job_id: str
    resume_text: str

@router.post("/score")
async def calculate_match_score(request: MatchRequest = Body(...)):
    # 1. Fetch the Job from MongoDB using the provided job_id
    try:
        job = await db["jobs"].find_one({"_id": ObjectId(request.job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Job ID format")

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    required_skills = [skill.lower() for skill in job.get("skills_required", [])]
    if not required_skills:
        return {"match_score": 0.0, "message": "This job has no required skills listed."}

    # 2. Process the resume text with spaCy
    doc = nlp(request.resume_text.lower())
    
    # 3. Extract exact skill matches
    # We check if the required skills are mentioned as tokens or entities in the resume
    resume_text_lower = request.resume_text.lower()
    matched_skills = [skill for skill in required_skills if skill in resume_text_lower]

    # 4. Calculate the Match Score (Percentage)
    score = (len(matched_skills) / len(required_skills)) * 100

    return {
        "job_id": request.job_id,
        "job_title": job.get("title"),
        "required_skills": required_skills,
        "candidate_matched_skills": matched_skills,
        "match_percentage": round(score, 2)
    }