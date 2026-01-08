from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import re

from app.database.database import get_db
from app.database.models import User
from app.utils.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_password
)
from app.utils.schemas import UserCreate, UserResponse

router = APIRouter()

# Regular expression for email validation
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


def is_valid_email(email: str) -> bool:
    """Validate email format using regex."""
    return re.match(EMAIL_REGEX, email) is not None


@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with hashed password."""
    # Validate email format
    if not is_valid_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Validate password length
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(id=user.id, email=user.email)


from pydantic import BaseModel

class LoginData(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(login_data: LoginData, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token using environment variable for expiration
    from app.utils.security import ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}