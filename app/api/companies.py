from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from app.schemas.company import CompanyCreate, CompanyResponse
from app.core.database import db # Assuming db is your Motor MongoDB client instance
from urllib.parse import urlparse

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", response_model=CompanyResponse)
async def create_company(company: CompanyCreate):
    # 1. Convert the Pydantic object into a Python dictionary
    company_dict = company.model_dump()
    
    # 2. Automated Verification Logic
    try:
        # Extract the domain from the website (e.g., "zagasoft.com")
        url_to_parse = company.website if "://" in company.website else f"http://{company.website}"
        website_domain = urlparse(url_to_parse).netloc.replace("www.", "").lower()
        
        # Extract the domain from the email (e.g., "zagasoft.com" from "hr@zagasoft.com")
        email_domain = company.official_email.split("@")[-1].lower()
        
        # If they match, mark as verified!
        company_dict["is_verified"] = (website_domain == email_domain)
    except Exception:
        # If anything goes wrong with parsing, default to False
        company_dict["is_verified"] = False

    # 3. Insert the dictionary into MongoDB
    result = await db["companies"].insert_one(company_dict)
    
    # 4. Attach the MongoDB generated ID to the dictionary and return it
    company_dict["id"] = str(result.inserted_id)
    return company_dict