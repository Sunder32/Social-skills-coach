"""
Chats API endpoints
Handles conversation preparation and dialogue simulation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.schemas.chat import (
    ConversationPrepareRequest, ConversationPrepareResponse,
    DialogueSimulationRequest, DialogueMessage, DialogueResponse,
    ChatHistory
)
from app.services.chat_service import ChatService
from app.services.user_service import UserService

router = APIRouter()


# Additional schemas for simple chat
class ChatCreateRequest(BaseModel):
    """Request to create a new chat"""
    title: Optional[str] = None
    type: str = "conversation"  # conversation, preparation, simulation, analysis


class MessageRequest(BaseModel):
    """Request to send a message"""
    content: str


@router.get("", response_model=List[ChatHistory])
async def get_all_chats(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get all user's chats"""
    service = ChatService(db)
    history = await service.get_history(current_user_id, limit, offset)
    return history


@router.post("", response_model=ChatHistory)
async def create_chat(
    request: ChatCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Create a new chat"""
    service = ChatService(db)
    chat = await service.create_chat(current_user_id, request.title, request.type)
    return chat


@router.post("/{chat_id}/messages", response_model=DialogueResponse)
async def send_message(
    chat_id: int,
    request: MessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Send a message in a chat"""
    service = ChatService(db)
    response = await service.send_message(chat_id, current_user_id, request.content)
    return response


@router.post("/prepare", response_model=ConversationPrepareResponse)
async def prepare_conversation(
    request: ConversationPrepareRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    AI-powered conversation preparation
    
    - **conversation_type**: Type (negotiation, conflict, request, rejection, introduction)
    - **situation**: Description of the situation
    - **interlocutor**: Description of the other person
    - **desired_outcome**: What you want to achieve
    - **concerns**: Your worries/fears about the conversation
    """
    service = ChatService(db)
    result = await service.prepare_conversation(current_user_id, request)
    return result


@router.post("/simulate", response_model=DialogueResponse)
async def simulate_dialogue(
    request: DialogueSimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Start or continue dialogue simulation with AI
    
    - **scenario**: Scenario description (for new dialogue)
    - **personality_type**: AI personality type (assertive, passive, aggressive, etc.)
    - **session_id**: Existing session ID to continue
    - **user_message**: User's message in the dialogue
    """
    service = ChatService(db)
    response = await service.simulate_dialogue(current_user_id, request)
    return response


@router.get("/history", response_model=List[ChatHistory])
async def get_chat_history(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get user's chat history"""
    service = ChatService(db)
    history = await service.get_history(current_user_id, limit, offset)
    return history


@router.get("/{chat_id}", response_model=ChatHistory)
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Get specific chat by ID"""
    service = ChatService(db)
    chat = await service.get_chat(chat_id, current_user_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Delete a chat"""
    service = ChatService(db)
    await service.delete_chat(chat_id, current_user_id)


@router.post("/{chat_id}/feedback")
async def submit_feedback(
    chat_id: int,
    rating: int,
    comment: str = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Submit feedback for a chat session (used for model training)"""
    service = ChatService(db)
    await service.save_feedback(chat_id, current_user_id, rating, comment)
    return {"status": "feedback saved"}
