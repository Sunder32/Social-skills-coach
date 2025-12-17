"""
Library API endpoints
Handles knowledge base search and retrieval
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.library import (
    KnowledgeItem, KnowledgeSearchResult,
    TopicResponse, TechniqueResponse
)
from app.services.library_service import LibraryService
from app.services.user_service import UserService

router = APIRouter()


@router.get("/search", response_model=KnowledgeSearchResult)
async def search_knowledge(
    query: str = Query(..., min_length=2, description="Search query"),
    topic: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Search the knowledge library
    
    - **query**: Search text
    - **topic**: Optional topic filter
    - **limit**: Number of results (1-50)
    
    Uses hybrid search: MySQL FULLTEXT + FAISS semantic search
    """
    service = LibraryService(db)
    results = await service.search(query, topic, limit)
    return results


@router.get("/topics", response_model=List[TopicResponse])
async def get_topics(
    db: AsyncSession = Depends(get_db)
):
    """Get all available topics in the knowledge base"""
    service = LibraryService(db)
    topics = await service.get_topics()
    return topics


@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get topic details with related content"""
    service = LibraryService(db)
    topic = await service.get_topic_by_id(topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    return topic


@router.get("/techniques", response_model=List[TechniqueResponse])
async def get_techniques(
    situation: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get communication techniques
    
    - **situation**: Optional filter by situation type
    """
    service = LibraryService(db)
    techniques = await service.get_techniques(situation)
    return techniques


@router.get("/techniques/{technique_id}", response_model=TechniqueResponse)
async def get_technique(
    technique_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed technique information"""
    service = LibraryService(db)
    technique = await service.get_technique_by_id(technique_id)
    
    if not technique:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technique not found"
        )
    
    return technique


@router.get("/item/{item_id}", response_model=KnowledgeItem)
async def get_knowledge_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific knowledge item by ID"""
    service = LibraryService(db)
    item = await service.get_item_by_id(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item


@router.get("/recommendations")
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get personalized content recommendations based on user profile and history"""
    service = LibraryService(db)
    recommendations = await service.get_recommendations(current_user_id)
    return recommendations
