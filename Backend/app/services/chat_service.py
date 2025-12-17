"""
Chat service - handles conversation preparation and simulation
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime

from app.models.chat import Chat, ChatMessage
from app.schemas.chat import (
    ConversationPrepareRequest, ConversationPrepareResponse,
    DialogueSimulationRequest, DialogueResponse, ChatHistory
)
from app.services.ai_service import AIService


class ChatService:
    """Service for handling chat operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
    
    async def prepare_conversation(
        self, 
        user_id: int, 
        request: ConversationPrepareRequest
    ) -> ConversationPrepareResponse:
        """Prepare for a conversation using AI"""
        
        # Generate plan using AI
        plan_data = await self.ai_service.generate_conversation_plan(
            conversation_type=request.conversation_type.value,
            situation=request.situation,
            interlocutor=request.interlocutor,
            desired_outcome=request.desired_outcome,
            concerns=request.concerns
        )
        
        # Save to database
        chat = Chat(
            user_id=user_id,
            type="preparation",
            title=f"Подготовка: {request.conversation_type.value}",
            conversation_type=request.conversation_type.value,
            situation=request.situation,
            plan=plan_data,
            chat_metadata={
                "interlocutor": request.interlocutor,
                "desired_outcome": request.desired_outcome,
                "concerns": request.concerns
            }
        )
        
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        
        return ConversationPrepareResponse(
            id=chat.id,
            situation_analysis=plan_data.get("situation_analysis", ""),
            emotional_assessment=plan_data.get("emotional_assessment", ""),
            plan=plan_data.get("plan", []),
            scenarios=plan_data.get("scenarios", []),
            objection_handling=plan_data.get("objection_handling", []),
            psychological_techniques=plan_data.get("psychological_techniques", []),
            dos_and_donts=plan_data.get("dos_and_donts", {}),
            created_at=chat.created_at
        )
    
    async def simulate_dialogue(
        self, 
        user_id: int, 
        request: DialogueSimulationRequest
    ) -> DialogueResponse:
        """Simulate a dialogue with AI"""
        
        # Get or create session
        if request.session_id:
            # Continue existing session
            result = await self.db.execute(
                select(Chat).where(
                    Chat.id == request.session_id,
                    Chat.user_id == user_id
                )
            )
            chat = result.scalar_one_or_none()
            
            if not chat:
                raise ValueError("Session not found")
            
            # Get message history
            messages_result = await self.db.execute(
                select(ChatMessage)
                .where(ChatMessage.chat_id == chat.id)
                .order_by(ChatMessage.created_at)
            )
            messages = messages_result.scalars().all()
            history = [{"role": m.role, "content": m.content} for m in messages]
            
        else:
            # Create new session
            chat = Chat(
                user_id=user_id,
                type="simulation",
                title=f"Симуляция: {request.personality_type.value}",
                personality_type=request.personality_type.value,
                scenario=request.scenario
            )
            
            self.db.add(chat)
            await self.db.flush()
            
            history = []
            
            # Add system message
            system_message = ChatMessage(
                chat_id=chat.id,
                role="system",
                content=f"Scenario: {request.scenario}"
            )
            self.db.add(system_message)
        
        # Save user message if provided
        if request.user_message:
            user_msg = ChatMessage(
                chat_id=chat.id,
                role="user",
                content=request.user_message
            )
            self.db.add(user_msg)
            history.append({"role": "user", "content": request.user_message})
        
        # Generate AI response
        ai_response = await self.ai_service.generate_dialogue_response(
            personality_type=request.personality_type.value,
            scenario=request.scenario or chat.scenario,
            history=history
        )
        
        # Save AI message
        ai_msg = ChatMessage(
            chat_id=chat.id,
            role="assistant",
            content=ai_response["message"],
            analysis=ai_response.get("user_message_analysis")
        )
        self.db.add(ai_msg)
        
        await self.db.commit()
        await self.db.refresh(chat)
        
        return DialogueResponse(
            session_id=chat.id,
            ai_message=ai_response["message"],
            message_analysis=ai_response.get("user_message_analysis"),
            suggestions=ai_response.get("suggestions"),
            session_complete=ai_response.get("session_complete", False),
            final_feedback=ai_response.get("final_feedback")
        )
    
    async def get_history(
        self, 
        user_id: int, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[ChatHistory]:
        """Get user's chat history"""
        result = await self.db.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(desc(Chat.created_at))
            .offset(offset)
            .limit(limit)
        )
        chats = result.scalars().all()
        
        return [
            ChatHistory(
                id=chat.id,
                type=chat.type,
                title=chat.title or "Untitled",
                preview=chat.situation[:100] if chat.situation else "",
                created_at=chat.created_at,
                updated_at=chat.updated_at
            )
            for chat in chats
        ]
    
    async def get_chat(self, chat_id: int, user_id: int) -> Optional[ChatHistory]:
        """Get specific chat with messages"""
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        chat = result.scalar_one_or_none()
        
        if not chat:
            return None
        
        # Get messages
        messages_result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at)
        )
        messages = messages_result.scalars().all()
        
        return ChatHistory(
            id=chat.id,
            type=chat.type,
            title=chat.title or "Untitled",
            preview=chat.situation[:100] if chat.situation else "",
            messages=[
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.created_at,
                    "analysis": m.analysis
                }
                for m in messages if m.role != "system"
            ],
            created_at=chat.created_at,
            updated_at=chat.updated_at
        )
    
    async def delete_chat(self, chat_id: int, user_id: int) -> None:
        """Delete a chat"""
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        chat = result.scalar_one_or_none()
        
        if chat:
            await self.db.delete(chat)
            await self.db.commit()
    
    async def save_feedback(
        self, 
        chat_id: int, 
        user_id: int, 
        rating: int, 
        comment: str = None
    ) -> None:
        """Save feedback for a chat session"""
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        chat = result.scalar_one_or_none()
        
        if chat:
            chat.feedback_rating = rating
            chat.feedback_comment = comment
            await self.db.commit()

    async def create_chat(
        self, 
        user_id: int, 
        title: str = None, 
        chat_type: str = "conversation"
    ) -> ChatHistory:
        """Create a new chat session"""
        chat = Chat(
            user_id=user_id,
            type=chat_type,
            title=title or "Новый разговор"
        )
        
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        
        return ChatHistory(
            id=chat.id,
            type=chat.type,
            title=chat.title,
            preview="",
            created_at=chat.created_at,
            updated_at=chat.updated_at
        )
    
    async def send_message(
        self, 
        chat_id: int, 
        user_id: int, 
        content: str
    ) -> DialogueResponse:
        """Send a message and get AI response"""
        # Get chat
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        chat = result.scalar_one_or_none()
        
        if not chat:
            raise ValueError("Chat not found")
        
        # Get message history
        messages_result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at)
        )
        messages = messages_result.scalars().all()
        history = [{"role": m.role, "content": m.content} for m in messages]
        
        # Save user message
        user_msg = ChatMessage(
            chat_id=chat.id,
            role="user",
            content=content
        )
        self.db.add(user_msg)
        history.append({"role": "user", "content": content})
        
        # Generate AI response
        ai_response = await self.ai_service.generate_chat_response(
            history=history,
            context=chat.situation
        )
        
        # Save AI message
        ai_msg = ChatMessage(
            chat_id=chat.id,
            role="assistant",
            content=ai_response["message"]
        )
        self.db.add(ai_msg)
        
        await self.db.commit()
        
        return DialogueResponse(
            session_id=chat.id,
            ai_message=ai_response["message"],
            message_analysis=ai_response.get("analysis"),
            suggestions=ai_response.get("suggestions"),
            session_complete=False,
            final_feedback=None
        )
