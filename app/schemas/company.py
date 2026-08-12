from pydantic import BaseModel
from typing import Optional

class CompanyCreate(BaseModel):
    name: str
    industry: str
    website: str
    description: str
    # Add the new required fields here
    registration_id: str 
    official_email: str 

class CompanyResponse(CompanyCreate):
    id: str
    is_verified: bool = False # Will default to False until our logic checks it

    class Config:
        from_attributes = True