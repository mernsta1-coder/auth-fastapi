from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.orm import Session
from app.models.user import User
from app.schema.user_schema import UserCreate, UserOut, LoginSchema
from app.database.database import SessionLocal
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.database.database import get_db
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=TokenResponse)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    ACCESS_TOKEN_EXPIRE_MINUTES = 90
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
   
    payload = {"sub": str(user.id), "exp": expire}
    
    ALGORITHM= os.getenv("ALGORITHM")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY").replace("\\n", "\n").strip()
    

    token = jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer()


@router.get("/profile", summary="Get user profile")
def get_profile(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials if credentials else None
   
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user_payload = getattr(request.state, "user", None)
    
    if not user_payload:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {
        "user_id": user_payload.get("sub"),
        "swagger_token": token  
    }