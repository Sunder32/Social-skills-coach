"""
Chat schemas for conversation preparation and simulation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ConversationType(str, Enum):
    """Types of conversations"""
    NEGOTIATION = "negotiation"
    CONFLICT = "conflict"
    REQUEST = "request"
    REJECTION = "rejection"
    INTRODUCTION = "introduction"
    FEEDBACK = "feedback"
    DIFFICULT_NEWS = "difficult_news"
    OTHER = "other"


class PersonalityType(str, Enum):
    """AI personality types for simulation"""
    ASSERTIVE = "assertive"
    PASSIVE = "passive"
    AGGRESSIVE = "aggressive"
    PASSIVE_AGGRESSIVE = "passive_aggressive"
    MANIPULATIVE = "manipulative"
    SUPPORTIVE = "supportive"
    SKEPTICAL = "skeptical"


class ConversationPrepareRequest(BaseModel):
    """Request schema for conversation preparation"""
    conversation_type: ConversationType
    situation: str = Field(..., min_length=10, max_length=2000)
    interlocutor: Optional[str] = Field(None, max_length=500)
    desired_outcome: str = Field(..., min_length=10, max_length=500)
    concerns: Optional[str] = Field(None, max_length=500)
    additional_context: Optional[str] = None


class ConversationPhase(BaseModel):
    """Single phase of conversation plan"""
    phase: str
    goals: List[str]
    key_phrases: List[str]
    techniques: List[str]
    warnings: Optional[List[str]] = None


class ScenarioBranch(BaseModel):
    """Possible scenario branch"""
    condition: str
    response_strategy: str
    key_phrases: List[str]


class ConversationPrepareResponse(BaseModel):
    """Response schema for conversation preparation"""
    id: int
    situation_analysis: str
    emotional_assessment: str
    plan: List[ConversationPhase]
    scenarios: List[ScenarioBranch]
    objection_handling: List[dict]
    psychological_techniques: List[str]
    dos_and_donts: dict
    created_at: datetime


class DialogueSimulationRequest(BaseModel):
    """Request for dialogue simulation"""
    session_id: Optional[int] = None  # None for new session
    scenario: Optional[str] = None  # Required for new session
    personality_type: PersonalityType = PersonalityType.ASSERTIVE
    user_message: Optional[str] = None  # User's message in dialogue


class DialogueMessage(BaseModel):
    """Single message in dialogue"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    analysis: Optional[dict] = None  # Real-time analysis of user's message


class DialogueResponse(BaseModel):
    """Response from dialogue simulation"""
    session_id: int
    ai_message: str
    message_analysis: Optional[dict] = None
    suggestions: Optional[List[str]] = None
    session_complete: bool = False
    final_feedback: Optional[dict] = None


class ChatHistory(BaseModel):
    """Chat history item"""
    id: int
    type: str  # "preparation" or "simulation"
    title: str
    preview: str
    messages: Optional[List[DialogueMessage]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
