"""
User schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """Schema for profile update"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    occupation: Optional[str] = Field(None, max_length=200)
    goals: Optional[List[str]] = None
    problem_areas: Optional[List[str]] = None
    skill_level: Optional[int] = Field(None, ge=1, le=10)
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    name: str
    occupation: Optional[str] = None
    goals: Optional[List[str]] = None
    problem_areas: Optional[List[str]] = None
    skill_level: Optional[int] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data"""
    user_id: int
    exp: datetime


class UserProgress(BaseModel):
    """Schema for user progress statistics"""
    total_conversations: int = 0
    total_analyses: int = 0
    total_exercises: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    skill_improvements: dict = {}
    recent_activity: List[dict] = []
    achievements: List[str] = []
