"""
User model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    
    occupation = Column(String(200))
    goals = Column(JSON)
    problem_areas = Column(JSON)
    skill_level = Column(Integer)
    avatar_url = Column(String(500))
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    reset_token = Column(String(500))
    reset_token_expires = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    exercise_completions = relationship("ExerciseCompletion", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
