from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

# ==========================================
# DATABASE CONNECTION
# ==========================================
# We must connect to the real database here so the routes can access it
client = MongoClient("mongodb://localhost:27017/")
db = client["ai_job_portal"]

# Create the router
router = APIRouter()

# --- Pydantic Model ---
class CompanyResponse(BaseModel):
    id: str
    name: str
    industry: str
    website: str
    registration_id: str
    official_email: str
    description: str
    is_verified: bool = False

# ==========================================
# ADMIN ENDPOINTS
# ==========================================
@router.get("/companies/pending")
def get_pending_companies():
    """Returns a list of all real companies from MongoDB where is_verified is False."""
    try:
        # Fetch from the REAL database instead of the fake list
        cursor = db.companies.find({"is_verified": {"$ne": True}})
        pending_companies = list(cursor) 
        
        for comp in pending_companies:
            comp["id"] = str(comp["_id"])
            del comp["_id"]
            
        return pending_companies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/companies/{company_id}/verify")
def verify_company(company_id: str):
    try:
        # Wrap company_id in ObjectId() so MongoDB understands it
        result = db.companies.update_one(
            {"_id": ObjectId(company_id)}, 
            {"$set": {"is_verified": True}}
        )
        
        # If modified_count is 0, it means it didn't find the document
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Company ID not found in database.")
            
        return {"message": "Company verified successfully!"}
        
    except InvalidId:
        # If the ID sent isn't a valid MongoDB ObjectId format, catch it gracefully
        raise HTTPException(status_code=400, detail="Invalid Company ID format. Must be a 24-character hex string.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))