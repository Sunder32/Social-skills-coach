"""
Users API endpoints
Handles user registration, authentication, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, UserProfileUpdate,
    Token, UserProgress
)
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    
    - **email**: User's email address
    - **password**: User's password (min 8 characters)
    - **name**: User's display name
    """
    service = UserService(db)
    
    # Check if user exists
    existing_user = await service.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    user = await service.create(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT token
    
    - **email**: User's email
    - **password**: User's password
    """
    service = UserService(db)
    
    user = await service.authenticate(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = service.create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get current user's profile"""
    service = UserService(db)
    user = await service.get_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Update user profile
    
    - **name**: Display name
    - **occupation**: User's occupation/field
    - **goals**: Communication goals
    - **problem_areas**: Areas to improve
    - **skill_level**: Self-assessed skill level (1-10)
    """
    service = UserService(db)
    user = await service.update_profile(current_user_id, profile_data)
    return user


@router.get("/progress", response_model=UserProgress)
async def get_progress(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get user's learning progress and statistics"""
    service = UserService(db)
    progress = await service.get_progress(current_user_id)
    return progress


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Delete user account and all associated data"""
    service = UserService(db)
    await service.delete(current_user_id)
