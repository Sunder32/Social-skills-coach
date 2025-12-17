"""
Library schemas for knowledge base
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KnowledgeItem(BaseModel):
    """Knowledge base item"""
    id: int
    title: str
    content: str
    source: Optional[str] = None  # Book/article reference
    topic_id: int
    topic_name: str
    tags: List[str] = []
    relevance_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeSearchResult(BaseModel):
    """Search results"""
    query: str
    total_results: int
    items: List[KnowledgeItem]
    suggestions: List[str] = []  # Related search suggestions


class TopicResponse(BaseModel):
    """Topic information"""
    id: int
    name: str
    description: str
    icon: Optional[str] = None
    item_count: int
    subtopics: List[str] = []

    class Config:
        from_attributes = True


class TechniqueResponse(BaseModel):
    """Communication technique"""
    id: int
    name: str
    description: str
    when_to_use: List[str]
    steps: List[str]
    examples: List[str]
    common_mistakes: List[str]
    related_techniques: List[str] = []
    situations: List[str] = []

    class Config:
        from_attributes = True
