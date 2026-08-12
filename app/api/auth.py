from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.database import users_collection
from app.api.dependencies import get_current_user

# Create a router instance for authentication endpoints
router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """
    Registers a new user, hashes their password, and saves to MongoDB.
    """
    # 1. Check if a user with this email already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email is already registered."
        )

    # 2. Hash the plaintext password
    hashed_password = get_password_hash(user.password)

    # 3. Convert the Pydantic model to a dictionary
    user_dict = user.model_dump()
    
    # 4. Replace the plaintext password with the hashed version before saving
    user_dict["password"] = hashed_password

    # 5. Insert the new user document into the MongoDB 'users' collection
    await users_collection.insert_one(user_dict)

    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns a JWT token.
    Uses OAuth2PasswordRequestForm to be compatible with Swagger UI.
    """
    # Note: OAuth2 strictly uses the field name 'username', 
    # so we map form_data.username to our database's email field.
    user = await users_collection.find_one({"email": form_data.username})
    
    # ⚠️ FIXED: We now check user["password"] to match how it is saved during registration
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate the JWT token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Protected route: Returns the profile data of the currently logged-in user.
    """
    return current_user