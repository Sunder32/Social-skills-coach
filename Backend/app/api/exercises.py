"""
Exercises API endpoints
Handles daily exercises and progress tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.schemas.exercises import (
    Exercise, ExerciseComplete, ExerciseProgress,
    DailyChallenge, StreakInfo
)
from app.services.exercises_service import ExercisesService
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=List[Exercise])
async def get_exercises(
    category: Optional[str] = None,
    difficulty: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Get available exercises
    
    - **category**: Filter by category (listening, assertiveness, empathy, etc.)
    - **difficulty**: Filter by difficulty level (1-5)
    """
    service = ExercisesService(db)
    exercises = await service.get_exercises(current_user_id, category, difficulty)
    return exercises


@router.get("/daily", response_model=DailyChallenge)
async def get_daily_challenge(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get today's personalized exercise challenge"""
    service = ExercisesService(db)
    challenge = await service.get_daily_challenge(current_user_id)
    return challenge


@router.get("/{exercise_id}", response_model=Exercise)
async def get_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get exercise details"""
    service = ExercisesService(db)
    exercise = await service.get_exercise_by_id(exercise_id)
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    return exercise


@router.post("/complete", response_model=ExerciseProgress)
async def complete_exercise(
    completion: ExerciseComplete,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Mark exercise as completed
    
    - **exercise_id**: ID of the completed exercise
    - **notes**: Optional notes/reflection
    - **rating**: Self-rating (1-5)
    - **time_spent**: Time spent in minutes
    """
    service = ExercisesService(db)
    progress = await service.complete_exercise(current_user_id, completion)
    return progress


@router.get("/progress/summary", response_model=ExerciseProgress)
async def get_progress_summary(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get overall exercise progress summary"""
    service = ExercisesService(db)
    summary = await service.get_progress_summary(current_user_id)
    return summary


@router.get("/progress/history")
async def get_progress_history(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get exercise history for a date range"""
    service = ExercisesService(db)
    history = await service.get_progress_history(current_user_id, start_date, end_date)
    return history


@router.get("/streak", response_model=StreakInfo)
async def get_streak(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get current streak information"""
    service = ExercisesService(db)
    streak = await service.get_streak(current_user_id)
    return streak


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all exercise categories"""
    service = ExercisesService(db)
    categories = await service.get_categories()
    return categories
