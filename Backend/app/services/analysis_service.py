"""
Analysis service - handles text analysis operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime
import io

from app.models.chat import Chat
from app.models.progress import Reflection
from app.schemas.analysis import (
    TextAnalysisRequest, TextAnalysisResponse,
    PostAnalysisRequest, PostAnalysisResponse,
    ReflectionEntry, ReflectionResponse,
    SentimentResult, MessageBalance
)
from app.services.ai_service import AIService


class AnalysisService:
    """Service for text analysis operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
    
    async def analyze_text(
        self, 
        user_id: int, 
        request: TextAnalysisRequest
    ) -> TextAnalysisResponse:
        """Analyze text for communication patterns"""
        
        # Perform AI analysis
        analysis = await self.ai_service.analyze_text(
            text=request.text,
            context=request.context
        )
        
        # Save as chat record
        chat = Chat(
            user_id=user_id,
            type="analysis",
            title="Анализ текста",
            situation=request.text[:500],
            chat_metadata={
                "context": request.context,
                "analysis_result": analysis
            }
        )
        
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        
        return TextAnalysisResponse(
            id=chat.id,
            sentiment=SentimentResult(**analysis["sentiment"]),
            patterns=analysis["patterns"],
            message_balance=MessageBalance(**analysis["message_balance"]),
            issues=analysis["issues"],
            strengths=analysis["strengths"],
            recommendations=analysis["recommendations"],
            alternatives=analysis["alternatives"],
            overall_assessment=analysis["overall_assessment"],
            created_at=chat.created_at
        )
    
    async def analyze_file(
        self,
        user_id: int,
        file_content: bytes,
        file_extension: str,
        context: Optional[str]
    ) -> TextAnalysisResponse:
        """Parse and analyze uploaded file"""
        
        # Parse file based on extension
        text = await self._parse_file(file_content, file_extension)
        
        # Use text analysis
        request = TextAnalysisRequest(text=text, context=context)
        return await self.analyze_text(user_id, request)
    
    async def _parse_file(self, content: bytes, extension: str) -> str:
        """Parse file content to text"""
        
        if extension == "txt":
            return content.decode("utf-8")
        
        elif extension == "docx":
            try:
                from docx import Document
                doc = Document(io.BytesIO(content))
                return "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                raise ValueError("DOCX parsing not available")
        
        elif extension == "pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(content))
                return "\n".join([page.extract_text() for page in reader.pages])
            except ImportError:
                raise ValueError("PDF parsing not available")
        
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    async def post_analysis(
        self,
        user_id: int,
        request: PostAnalysisRequest
    ) -> PostAnalysisResponse:
        """Perform post-conversation analysis"""
        
        # Get preparation plan if exists
        preparation_plan = None
        if request.preparation_id:
            result = await self.db.execute(
                select(Chat).where(
                    Chat.id == request.preparation_id,
                    Chat.user_id == user_id
                )
            )
            prep_chat = result.scalar_one_or_none()
            if prep_chat:
                preparation_plan = prep_chat.plan
        
        # Generate post-analysis
        analysis = await self.ai_service.generate_post_analysis(
            preparation_plan=preparation_plan,
            actual_outcome=request.actual_outcome,
            what_worked=request.what_worked,
            what_didnt_work=request.what_didnt_work,
            emotions=request.emotions
        )
        
        # Save as chat record
        chat = Chat(
            user_id=user_id,
            type="analysis",
            title="Пост-анализ разговора",
            situation=request.actual_outcome[:500],
            chat_metadata={
                "preparation_id": request.preparation_id,
                "what_worked": request.what_worked,
                "what_didnt_work": request.what_didnt_work,
                "emotions": request.emotions,
                "analysis_result": analysis
            }
        )
        
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        
        return PostAnalysisResponse(
            id=chat.id,
            plan_comparison=analysis.get("plan_comparison"),
            success_factors=analysis.get("success_factors", []),
            improvement_areas=analysis.get("improvement_areas", []),
            lessons_learned=analysis.get("lessons_learned", []),
            recommendations_for_future=analysis.get("recommendations_for_future", []),
            skill_progress=analysis.get("skill_progress", {}),
            created_at=chat.created_at
        )
    
    async def save_reflection(
        self,
        user_id: int,
        entry: ReflectionEntry
    ) -> ReflectionResponse:
        """Save a reflection diary entry"""
        
        # Generate AI insights (optional)
        ai_insights = None
        try:
            insights = await self.ai_service.llm_client.generate_reflection_insights(
                content=entry.content,
                mood=entry.mood
            )
            ai_insights = insights.get("insights")
        except:
            pass
        
        reflection = Reflection(
            user_id=user_id,
            content=entry.content,
            mood=entry.mood,
            tags=entry.tags or [],
            ai_insights=ai_insights,
            related_chat_id=entry.related_conversation_id
        )
        
        self.db.add(reflection)
        await self.db.commit()
        await self.db.refresh(reflection)
        
        return ReflectionResponse(
            id=reflection.id,
            content=reflection.content,
            mood=reflection.mood,
            tags=reflection.tags or [],
            ai_insights=reflection.ai_insights,
            created_at=reflection.created_at
        )
    
    async def get_reflections(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[ReflectionResponse]:
        """Get user's reflection entries"""
        
        result = await self.db.execute(
            select(Reflection)
            .where(Reflection.user_id == user_id)
            .order_by(desc(Reflection.created_at))
            .offset(offset)
            .limit(limit)
        )
        reflections = result.scalars().all()
        
        return [
            ReflectionResponse(
                id=r.id,
                content=r.content,
                mood=r.mood,
                tags=r.tags or [],
                ai_insights=r.ai_insights,
                created_at=r.created_at
            )
            for r in reflections
        ]
