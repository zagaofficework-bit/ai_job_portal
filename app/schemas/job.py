from pydantic import BaseModel
from typing import List

class JobCreate(BaseModel):
    title: str
    description: str
    skills_required: List[str]  # e.g., ["Python", "FastAPI", "MongoDB"]
    experience_years: int
    company_id: str  # The reference link to the Company

class JobResponse(JobCreate):
    id: str

    class Config:
        from_attributes = True