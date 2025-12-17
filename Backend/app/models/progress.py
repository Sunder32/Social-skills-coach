"""
Progress and exercise tracking models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Progress(Base):
    """User progress tracking"""
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Statistics
    total_conversations = Column(Integer, default=0)
    total_analyses = Column(Integer, default=0)
    total_exercises = Column(Integer, default=0)
    total_time_spent = Column(Integer, default=0)  # minutes
    
    # Streaks
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(Date)
    streak_started = Column(Date)
    
    # Skill tracking (JSON: skill_name -> score)
    skill_levels = Column(JSON, default={})
    skill_history = Column(JSON, default=[])  # List of {date, skill, change}
    
    # Achievements
    achievements = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")

    def __repr__(self):
        return f"<Progress user={self.user_id}>"


class ExerciseCompletion(Base):
    """Exercise completion records"""
    __tablename__ = "exercise_completions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    # Completion data
    rating = Column(Integer)  # 1-5 self-rating
    notes = Column(Text)
    time_spent = Column(Integer)  # minutes
    
    # Timestamps
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="exercise_completions")
    exercise = relationship("Exercise")

    def __repr__(self):
        return f"<ExerciseCompletion user={self.user_id} exercise={self.exercise_id}>"


class Exercise(Base):
    """Exercise definitions"""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    category = Column(String(100), nullable=False, index=True)
    difficulty = Column(Integer, nullable=False)  # 1-5
    duration_minutes = Column(Integer, default=10)
    
    instructions = Column(JSON)  # List of instruction steps
    tips = Column(JSON)  # List of tips
    skill_targets = Column(JSON)  # List of targeted skills
    
    # Metadata
    is_active = Column(Integer, default=1)
    order_index = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Exercise {self.title}>"


class Reflection(Base):
    """Reflection diary entries"""
    __tablename__ = "reflections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    content = Column(Text, nullable=False)
    mood = Column(Integer)  # 1-10
    tags = Column(JSON)  # List of tags
    
    # AI analysis
    ai_insights = Column(Text)
    
    # Related conversation
    related_chat_id = Column(Integer, ForeignKey("chats.id", ondelete="SET NULL"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Reflection {self.id}>"
