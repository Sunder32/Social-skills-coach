"""
Analysis schemas for text analysis and reflection
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TextAnalysisRequest(BaseModel):
    """Request for text analysis"""
    text: str = Field(..., min_length=10, max_length=10000)
    context: Optional[str] = Field(None, max_length=500)


class SentimentResult(BaseModel):
    """Sentiment analysis result"""
    overall: str  # positive, negative, neutral, mixed
    score: float  # -1 to 1
    emotions: dict  # detected emotions with scores
    tone: str  # formal, informal, aggressive, passive, etc.


class CommunicationPattern(BaseModel):
    """Detected communication pattern"""
    pattern_type: str
    description: str
    examples: List[str]
    frequency: int
    impact: str  # positive, negative, neutral


class MessageBalance(BaseModel):
    """I-messages vs You-messages analysis"""
    i_messages_count: int
    you_messages_count: int
    i_messages_percentage: float
    examples_i: List[str]
    examples_you: List[str]
    recommendation: str


class DetectedIssue(BaseModel):
    """Detected communication issue"""
    issue_type: str  # passive_aggression, manipulation, blame, etc.
    severity: str  # low, medium, high
    evidence: List[str]
    explanation: str
    suggestion: str


class AlternativePhrase(BaseModel):
    """Suggested alternative phrasing"""
    original: str
    alternatives: List[str]
    explanation: str


class TextAnalysisResponse(BaseModel):
    """Response for text analysis"""
    id: int
    sentiment: SentimentResult
    patterns: List[CommunicationPattern]
    message_balance: MessageBalance
    issues: List[DetectedIssue]
    strengths: List[str]
    recommendations: List[str]
    alternatives: List[AlternativePhrase]
    overall_assessment: str
    created_at: datetime


class PostAnalysisRequest(BaseModel):
    """Request for post-conversation analysis"""
    preparation_id: Optional[int] = None
    actual_outcome: str = Field(..., min_length=10)
    what_worked: Optional[str] = None
    what_didnt_work: Optional[str] = None
    emotions: Optional[str] = None
    other_person_reaction: Optional[str] = None


class PostAnalysisResponse(BaseModel):
    """Response for post-conversation analysis"""
    id: int
    plan_comparison: Optional[dict] = None
    success_factors: List[str]
    improvement_areas: List[str]
    lessons_learned: List[str]
    recommendations_for_future: List[str]
    skill_progress: dict
    created_at: datetime


class ReflectionEntry(BaseModel):
    """Reflection diary entry"""
    content: str = Field(..., min_length=10, max_length=5000)
    mood: int = Field(..., ge=1, le=10)
    tags: Optional[List[str]] = None
    related_conversation_id: Optional[int] = None


class ReflectionResponse(BaseModel):
    """Response for saved reflection"""
    id: int
    content: str
    mood: int
    tags: List[str]
    ai_insights: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
