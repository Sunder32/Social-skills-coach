"""
Exercises service - handles exercises and progress tracking
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from datetime import date, datetime, timedelta

from app.models.progress import Exercise, ExerciseCompletion, Progress
from app.schemas.exercises import (
    Exercise as ExerciseSchema,
    ExerciseComplete, ExerciseProgress,
    DailyChallenge, StreakInfo
)


class ExercisesService:
    """Service for exercise operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_exercises(
        self,
        user_id: int,
        category: Optional[str] = None,
        difficulty: Optional[int] = None
    ) -> List[ExerciseSchema]:
        """Get available exercises"""
        
        # Get user's completed exercises
        completed_result = await self.db.execute(
            select(ExerciseCompletion.exercise_id)
            .where(ExerciseCompletion.user_id == user_id)
        )
        completed_ids = {row[0] for row in completed_result.all()}
        
        # Build query
        stmt = select(Exercise).where(Exercise.is_active == 1)
        
        if category:
            stmt = stmt.where(Exercise.category == category)
        
        if difficulty:
            stmt = stmt.where(Exercise.difficulty == difficulty)
        
        stmt = stmt.order_by(Exercise.order_index)
        
        result = await self.db.execute(stmt)
        exercises = result.scalars().all()
        
        return [
            ExerciseSchema(
                id=e.id,
                title=e.title,
                description=e.description,
                category=e.category,
                difficulty=e.difficulty,
                duration_minutes=e.duration_minutes,
                instructions=e.instructions or [],
                tips=e.tips or [],
                skill_targets=e.skill_targets or [],
                is_completed=e.id in completed_ids
            )
            for e in exercises
        ]
    
    async def get_exercise_by_id(self, exercise_id: int) -> Optional[ExerciseSchema]:
        """Get exercise by ID"""
        
        result = await self.db.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        e = result.scalar_one_or_none()
        
        if not e:
            return None
        
        return ExerciseSchema(
            id=e.id,
            title=e.title,
            description=e.description,
            category=e.category,
            difficulty=e.difficulty,
            duration_minutes=e.duration_minutes,
            instructions=e.instructions or [],
            tips=e.tips or [],
            skill_targets=e.skill_targets or []
        )
    
    async def get_daily_challenge(self, user_id: int) -> DailyChallenge:
        """Get personalized daily challenge"""
        
        # Get user's progress
        progress_result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = progress_result.scalar_one_or_none()
        
        # Get completed exercises
        completed_result = await self.db.execute(
            select(ExerciseCompletion.exercise_id)
            .where(ExerciseCompletion.user_id == user_id)
        )
        completed_ids = {row[0] for row in completed_result.all()}
        
        # Find suitable exercise
        stmt = select(Exercise).where(
            Exercise.is_active == 1,
            ~Exercise.id.in_(completed_ids) if completed_ids else True
        ).order_by(func.random()).limit(1)
        
        result = await self.db.execute(stmt)
        exercise = result.scalar_one_or_none()
        
        if not exercise:
            # All exercises completed, pick random
            result = await self.db.execute(
                select(Exercise)
                .where(Exercise.is_active == 1)
                .order_by(func.random())
                .limit(1)
            )
            exercise = result.scalar_one_or_none()
        
        # Calculate expiry (end of day)
        now = datetime.now()
        expiry = datetime(now.year, now.month, now.day, 23, 59, 59)
        
        streak_bonus = None
        if progress and progress.current_streak >= 7:
            streak_bonus = f"🔥 {progress.current_streak} дней подряд! Продолжайте!"
        
        return DailyChallenge(
            exercise=ExerciseSchema(
                id=exercise.id,
                title=exercise.title,
                description=exercise.description,
                category=exercise.category,
                difficulty=exercise.difficulty,
                duration_minutes=exercise.duration_minutes,
                instructions=exercise.instructions or [],
                tips=exercise.tips or [],
                skill_targets=exercise.skill_targets or []
            ),
            reason="Рекомендовано на основе вашего прогресса",
            streak_bonus=streak_bonus,
            expiry=expiry
        )
    
    async def complete_exercise(
        self,
        user_id: int,
        completion: ExerciseComplete
    ) -> ExerciseProgress:
        """Mark exercise as completed"""
        
        # Create completion record
        exercise_completion = ExerciseCompletion(
            user_id=user_id,
            exercise_id=completion.exercise_id,
            rating=completion.rating,
            notes=completion.notes,
            time_spent=completion.time_spent
        )
        
        self.db.add(exercise_completion)
        
        # Update progress
        progress_result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = progress_result.scalar_one_or_none()
        
        if progress:
            progress.total_exercises += 1
            progress.total_time_spent += completion.time_spent or 0
            
            # Update streak
            today = date.today()
            if progress.last_activity_date:
                days_diff = (today - progress.last_activity_date).days
                
                if days_diff == 1:
                    progress.current_streak += 1
                elif days_diff > 1:
                    progress.current_streak = 1
                    progress.streak_started = today
            else:
                progress.current_streak = 1
                progress.streak_started = today
            
            progress.last_activity_date = today
            
            if progress.current_streak > progress.longest_streak:
                progress.longest_streak = progress.current_streak
        
        await self.db.commit()
        
        return await self.get_progress_summary(user_id)
    
    async def get_progress_summary(self, user_id: int) -> ExerciseProgress:
        """Get exercise progress summary"""
        
        # Get progress
        progress_result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = progress_result.scalar_one_or_none()
        
        # Count total exercises
        total_result = await self.db.execute(
            select(func.count(Exercise.id)).where(Exercise.is_active == 1)
        )
        total_available = total_result.scalar() or 0
        
        # Count completed
        completed_result = await self.db.execute(
            select(func.count(ExerciseCompletion.id))
            .where(ExerciseCompletion.user_id == user_id)
        )
        total_completed = completed_result.scalar() or 0
        
        # Average rating
        rating_result = await self.db.execute(
            select(func.avg(ExerciseCompletion.rating))
            .where(ExerciseCompletion.user_id == user_id)
        )
        avg_rating = rating_result.scalar() or 0
        
        # Category progress
        category_result = await self.db.execute(
            select(
                Exercise.category,
                func.count(ExerciseCompletion.id)
            )
            .join(ExerciseCompletion, Exercise.id == ExerciseCompletion.exercise_id)
            .where(ExerciseCompletion.user_id == user_id)
            .group_by(Exercise.category)
        )
        categories = {cat: count for cat, count in category_result.all()}
        
        # Weekly completions (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        weekly_result = await self.db.execute(
            select(func.date(ExerciseCompletion.completed_at), func.count(ExerciseCompletion.id))
            .where(
                ExerciseCompletion.user_id == user_id,
                ExerciseCompletion.completed_at >= week_ago
            )
            .group_by(func.date(ExerciseCompletion.completed_at))
        )
        weekly_data = dict(weekly_result.all())
        
        weekly_completions = []
        for i in range(7):
            day = (datetime.now() - timedelta(days=6-i)).date()
            weekly_completions.append(weekly_data.get(day, 0))
        
        completion_rate = (total_completed / total_available * 100) if total_available > 0 else 0
        
        return ExerciseProgress(
            total_completed=total_completed,
            total_available=total_available,
            completion_rate=round(completion_rate, 1),
            average_rating=round(float(avg_rating), 1),
            total_time_spent=progress.total_time_spent if progress else 0,
            categories_progress=categories,
            skill_progress=progress.skill_levels if progress else {},
            weekly_completions=weekly_completions
        )
    
    async def get_progress_history(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[dict]:
        """Get exercise history for date range"""
        
        stmt = select(ExerciseCompletion, Exercise).join(Exercise).where(
            ExerciseCompletion.user_id == user_id
        )
        
        if start_date:
            stmt = stmt.where(ExerciseCompletion.completed_at >= start_date)
        
        if end_date:
            stmt = stmt.where(ExerciseCompletion.completed_at <= end_date)
        
        stmt = stmt.order_by(desc(ExerciseCompletion.completed_at))
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "id": completion.id,
                "exercise_id": completion.exercise_id,
                "exercise_title": exercise.title,
                "category": exercise.category,
                "rating": completion.rating,
                "notes": completion.notes,
                "time_spent": completion.time_spent,
                "completed_at": completion.completed_at
            }
            for completion, exercise in rows
        ]
    
    async def get_streak(self, user_id: int) -> StreakInfo:
        """Get streak information"""
        
        progress_result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = progress_result.scalar_one_or_none()
        
        if not progress:
            return StreakInfo(
                current_streak=0,
                longest_streak=0,
                next_milestone=7,
                rewards=[]
            )
        
        # Calculate next milestone
        milestones = [7, 14, 30, 60, 100, 365]
        next_milestone = 7
        for m in milestones:
            if progress.current_streak < m:
                next_milestone = m
                break
        
        # Calculate rewards
        rewards = []
        if progress.longest_streak >= 7:
            rewards.append("🔥 Неделя подряд")
        if progress.longest_streak >= 30:
            rewards.append("🏆 Месяц практики")
        if progress.longest_streak >= 100:
            rewards.append("⭐ 100 дней!")
        
        return StreakInfo(
            current_streak=progress.current_streak,
            longest_streak=progress.longest_streak,
            last_activity_date=progress.last_activity_date,
            streak_started=progress.streak_started,
            next_milestone=next_milestone,
            rewards=rewards
        )
    
    async def get_categories(self) -> List[dict]:
        """Get all exercise categories"""
        
        result = await self.db.execute(
            select(
                Exercise.category,
                func.count(Exercise.id).label("count")
            )
            .where(Exercise.is_active == 1)
            .group_by(Exercise.category)
        )
        
        return [
            {"name": cat, "count": count}
            for cat, count in result.all()
        ]
