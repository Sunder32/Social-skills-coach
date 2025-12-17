"""
User model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    
    # Profile
    occupation = Column(String(200))
    goals = Column(JSON)  # List of goals
    problem_areas = Column(JSON)  # List of problem areas
    skill_level = Column(Integer)  # 1-10 self-assessment
    avatar_url = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    exercise_completions = relationship("ExerciseCompletion", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
