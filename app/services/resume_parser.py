import spacy
import io
import re
from PyPDF2 import PdfReader

# 1. Load the pre-trained English NLP model into memory
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model not found. Please run: python -m spacy download en_core_web_sm")

# 2. Add an EntityRuler to teach spaCy about specific technical skills
if "entity_ruler" not in nlp.pipe_names:
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    
    # Custom skill list relevant to the tech stack and candidate profiles
    tech_skills = [
        "Python", "Java", "FastAPI", "MongoDB", "SQL", 
        "Machine Learning", "NLP", "spaCy", "C++", 
        "JavaScript", "React", "Node.js"
    ]
    
    # Create rule patterns so the AI flags these words as "SKILL"
    patterns = [
        {"label": "SKILL", "pattern": [{"LOWER": skill.lower()}]} 
        for skill in tech_skills
    ]
    
    ruler.add_patterns(patterns)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Reads a PDF file directly from memory and extracts the raw text."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + " "
    
    # Clean up excess whitespace
    return " ".join(text.split())

def parse_resume(text: str) -> dict:
    """Uses spaCy to analyze the text and extract structured entities."""
    # Feed the raw text into our customized NLP brain
    doc = nlp(text)
    
    # Use standard Python regex for highly predictable patterns like emails
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    
    # Let spaCy dynamically categorize entities (now including our "SKILL" label)
    entities = {}
    for ent in doc.ents:
        # Group entities by their AI-assigned label
        if ent.label_ not in entities:
            entities[ent.label_] = []
        
        # Avoid duplicates
        if ent.text.strip() not in entities[ent.label_]:
            entities[ent.label_].append(ent.text.strip())
            
    return {
        "contact_emails": list(set(emails)), # set() ensures no duplicate emails
        "spacy_entities": entities,
        "word_count": len(doc)
    }