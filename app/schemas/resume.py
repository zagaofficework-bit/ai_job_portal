from pydantic import BaseModel
from typing import List, Dict


class ResumeData(BaseModel):
    user_id: str
    filename: str
    contact_emails: List[str] = []
    skills: List[str] = []         
    raw_entities: Dict[str, list]  
    word_count: int