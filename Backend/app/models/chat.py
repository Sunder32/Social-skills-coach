"""
Chat and message models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class ChatType(str, enum.Enum):
    """Chat types"""
    PREPARATION = "preparation"
    SIMULATION = "simulation"
    ANALYSIS = "analysis"


class Chat(Base):
    """Chat/conversation session model"""
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    type = Column(String(50), nullable=False)  # preparation, simulation, analysis
    title = Column(String(255))
    
    # For preparation
    conversation_type = Column(String(50))  # negotiation, conflict, etc.
    situation = Column(Text)
    plan = Column(JSON)  # Generated plan
    
    # For simulation
    personality_type = Column(String(50))
    scenario = Column(Text)
    
    # Metadata
    metadata = Column(JSON)
    feedback_rating = Column(Integer)  # User feedback 1-5
    feedback_comment = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chat {self.id} - {self.type}>"


class ChatMessage(Base):
    """Individual message in a chat"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Analysis of user messages
    analysis = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage {self.id} - {self.role}>"
