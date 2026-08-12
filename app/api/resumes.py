from fastapi import APIRouter, UploadFile, Form, File, HTTPException, Depends, status
from app.api.dependencies import get_current_user
from app.services.resume_parser import extract_text_from_pdf, parse_resume
from app.schemas.resume import ResumeData
from typing import List

# IMPORTANT: Import your database instance here! 
from app.core.database import db 

router = APIRouter()

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """
    Protected route: Accepts a PDF resume, extracts the text, runs NLP, and saves to MongoDB.
    """
    # 1. Validate the file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported."
        )
    
    try:
        # 2. Read the file into memory asynchronously
        file_bytes = await file.read()
        
        # 3. Extract text using our service
        raw_text = extract_text_from_pdf(file_bytes)
        
        if not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract text from the PDF. It might be an image-based PDF."
            )
            
        # 4. Parse the text with spaCy
        ai_analysis = parse_resume(raw_text)
        
        # 5. Extract just the skills list for our Pydantic model
        extracted_skills = ai_analysis["spacy_entities"].get("SKILL", [])
        
        # 6. Validate and format the data using our new schema
        resume_doc = ResumeData(
            user_id=str(current_user["_id"]),
            filename=file.filename,
            contact_emails=ai_analysis["contact_emails"],
            skills=extracted_skills,
            raw_entities=ai_analysis["spacy_entities"],
            word_count=ai_analysis["word_count"]
        )
        
        # 7. Save to MongoDB (Converting Pydantic model to a dictionary)
        result = await db["resumes"].insert_one(resume_doc.model_dump())
        
        # 8. Return the final success response alongside the new database ID
        return {
            "message": "Resume processed and saved to database successfully",
            "resume_id": str(result.inserted_id),
            "data": resume_doc.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the file: {str(e)}"
        )

        @router.post("/analyze")
        async def analyze_resume(
            # File(...) catches the uploaded PDF/TXT document
            file: UploadFile = File(...), 
    
            # Form(...) catches the text area input for the job description
            job_description: str = Form(...) 
        ):
            try:
                # 1. Read the uploaded file into memory
                file_bytes = await file.read()
        
                # 2. Extract the text (Logic to be added later)
                # If it's a PDF, we will use a library like PyPDF2 or pdfplumber here.
                # If it's a TXT, we can decode it directly.

                # 3. Send to AI for processing (Logic to be added later)
                # This is where we will pass the extracted text and the job_description
                # to an AI model to get the actual dynamic score.

                # 4. Return the response in the exact JSON structure the frontend expects
                return {
                    "filename": file.filename,
                    "match_score": 85,  # Mock score for testing the UI
                    "feedback": "The candidate has strong backend experience. Excellent architectural understanding, but lacks specific cloud deployment knowledge mentioned in the job description.",
                    "skills": ["Python", "FastAPI", "SQL", "Git", "System Design"]
                }
        
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")