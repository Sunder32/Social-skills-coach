"""
Exercises schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class Exercise(BaseModel):
    """Exercise item"""
    id: int
    title: str
    description: str
    category: str
    difficulty: int = Field(..., ge=1, le=5)
    duration_minutes: int
    instructions: List[str]
    tips: List[str]
    skill_targets: List[str]
    is_completed: bool = False

    class Config:
        from_attributes = True


class ExerciseComplete(BaseModel):
    """Exercise completion data"""
    exercise_id: int
    notes: Optional[str] = Field(None, max_length=1000)
    rating: int = Field(..., ge=1, le=5)
    time_spent: Optional[int] = None  # minutes


class ExerciseProgress(BaseModel):
    """Exercise progress summary"""
    total_completed: int
    total_available: int
    completion_rate: float
    average_rating: float
    total_time_spent: int  # minutes
    categories_progress: dict  # category -> completion %
    skill_progress: dict  # skill -> improvement score
    weekly_completions: List[int]  # last 7 days


class DailyChallenge(BaseModel):
    """Daily challenge"""
    exercise: Exercise
    reason: str  # Why this exercise was chosen
    streak_bonus: Optional[str] = None
    expiry: datetime


class StreakInfo(BaseModel):
    """Streak information"""
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date] = None
    streak_started: Optional[date] = None
    next_milestone: int
    rewards: List[str] = []
