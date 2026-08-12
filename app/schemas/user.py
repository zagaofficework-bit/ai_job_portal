from pydantic import BaseModel, EmailStr, Field

# --- REGISTRATION SCHEMAS ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(default="candidate")

class UserResponse(BaseModel):
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

# --- LOGIN SCHEMAS ---

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str