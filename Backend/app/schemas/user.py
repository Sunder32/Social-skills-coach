"""
Схемы пользователя для валидации запросов/ответов
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """Схема для обновления профиля"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    occupation: Optional[str] = Field(None, max_length=200)
    goals: Optional[List[str]] = None
    problem_areas: Optional[List[str]] = None
    skill_level: Optional[int] = Field(None, ge=1, le=10)
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    """Схема для ответа с данными пользователя"""
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
    """Схема для ответа с JWT токеном"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Схема для расшифрованных данных токена"""
    user_id: int
    exp: datetime


class UserProgress(BaseModel):
    """Схема для статистики прогресса пользователя"""
    total_conversations: int = 0
    total_analyses: int = 0
    total_exercises: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    skill_improvements: dict = {}
    recent_activity: List[dict] = []
    achievements: List[str] = []


class PasswordResetRequest(BaseModel):
    """Схема для запроса восстановления пароля"""
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class MessageResponse(BaseModel):
    message: str


class EmailVerification(BaseModel):
    """Схема для подтверждения email"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class ResendVerification(BaseModel):
    """Схема для повторной отправки кода"""
    email: EmailStr
