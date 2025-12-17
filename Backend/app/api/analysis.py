"""
Analysis API endpoints
Handles text analysis and correspondence evaluation
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.analysis import (
    TextAnalysisRequest, TextAnalysisResponse,
    PostAnalysisRequest, PostAnalysisResponse,
    ReflectionEntry, ReflectionResponse
)
from app.services.analysis_service import AnalysisService
from app.services.user_service import UserService
from app.config import settings

router = APIRouter()


@router.post("/text", response_model=TextAnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Analyze text/correspondence for communication patterns
    
    - **text**: Text to analyze (max 10,000 characters)
    - **context**: Optional context about the conversation
    
    Returns:
    - Sentiment analysis
    - Communication patterns
    - I-messages vs You-messages balance
    - Detected issues (passive aggression, manipulation, etc.)
    - Recommendations
    - Alternative phrasings
    """
    if len(request.text) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text exceeds maximum length of 10,000 characters"
        )
    
    service = AnalysisService(db)
    result = await service.analyze_text(current_user_id, request)
    return result


@router.post("/upload", response_model=TextAnalysisResponse)
async def analyze_uploaded_file(
    file: UploadFile = File(...),
    context: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Upload and analyze a document (TXT, DOCX, PDF)
    
    - **file**: Document file (max 10MB)
    - **context**: Optional context about the conversation
    """
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
        )
    
    # Validate file extension
    ext = file.filename.split('.')[-1].lower()
    allowed = settings.ALLOWED_EXTENSIONS.split(',')
    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed)}"
        )
    
    service = AnalysisService(db)
    result = await service.analyze_file(current_user_id, contents, ext, context)
    return result


@router.post("/post-analysis", response_model=PostAnalysisResponse)
async def post_conversation_analysis(
    request: PostAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Post-conversation analysis and reflection
    
    - **preparation_id**: ID of the preparation plan (if any)
    - **actual_outcome**: What actually happened
    - **what_worked**: What went well
    - **what_didnt_work**: What didn't go as planned
    - **emotions**: How you felt
    """
    service = AnalysisService(db)
    result = await service.post_analysis(current_user_id, request)
    return result


@router.post("/reflection", response_model=ReflectionResponse)
async def save_reflection(
    entry: ReflectionEntry,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Save a reflection diary entry
    
    - **content**: Reflection text
    - **mood**: Current mood (1-10)
    - **tags**: Optional tags for categorization
    """
    service = AnalysisService(db)
    result = await service.save_reflection(current_user_id, entry)
    return result


@router.get("/reflections")
async def get_reflections(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get user's reflection entries"""
    service = AnalysisService(db)
    reflections = await service.get_reflections(current_user_id, limit, offset)
    return reflections
