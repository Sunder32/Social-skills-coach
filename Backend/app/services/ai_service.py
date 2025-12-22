"""
AI Service - integrates with external AI API for all AI operations
Uses DASA AI API Server via HTTP
"""
import os
from typing import Dict, List, Any, Optional
import threading

from app.config import settings
from app.services.ai_api_client import AIAPIClient


class AIService:
    """
    Service for AI operations.
    Connects to external DASA AI API Server.
    """
    
    _instance = None
    _initialized = False
    _init_lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if AIService._initialized:
            return
        
        with AIService._init_lock:
            if not AIService._initialized:
                self._initialize_client()
                AIService._initialized = True
    
    def _initialize_client(self):
        """Initialize AI API client"""
        try:
            self.client = AIAPIClient()
            self._ai_available = True
            print("AI API Client initialized successfully")
        except Exception as e:
            print(f"Warning: AI API client initialization failed: {e}")
            self.client = None
            self._ai_available = False
    
    async def generate_conversation_plan(
        self,
        conversation_type: str,
        situation: str,
        interlocutor: Optional[str],
        desired_outcome: str,
        concerns: Optional[str]
    ) -> Dict[str, Any]:
        """Generate a conversation preparation plan"""
        
        if not self._ai_available or not self.client:
            return self._get_fallback_plan(conversation_type, situation)
        
        return await self.client.generate_conversation_plan(
            conversation_type=conversation_type,
            situation=situation,
            interlocutor=interlocutor,
            desired_outcome=desired_outcome,
            concerns=concerns
        )
    
    async def generate_dialogue_response(
        self,
        personality_type: str,
        scenario: str,
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate AI response in dialogue simulation"""
        
        if not self._ai_available or not self.client:
            return self._get_fallback_response(personality_type)
        
        response = await self.client.generate_dialogue_response(
            personality_type=personality_type,
            scenario=scenario,
            history=history
        )
        
        return {
            "message": response.get("message", ""),
            "user_message_analysis": response.get("user_message_analysis"),
            "suggestions": response.get("suggestions"),
            "session_complete": response.get("session_complete", False),
            "final_feedback": response.get("final_feedback")
        }
    
    async def analyze_text(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze text for communication patterns"""
        
        if not self._ai_available or not self.client:
            return self._get_fallback_analysis()
        
        result = await self.client.analyze_text(text, context)
        
        return {
            "sentiment": result.get("sentiment", {}),
            "patterns": result.get("patterns", {}),
            "message_balance": result.get("message_balance", {}),
            "issues": result.get("issues", []),
            "strengths": [],
            "recommendations": result.get("recommendations", []),
            "alternatives": [],
            "overall_assessment": ""
        }
    
    async def analyze_user_message(self, message: str) -> Dict[str, Any]:
        """Quick analysis of user's message in dialogue"""
        
        if not self._ai_available or not self.client:
            return {}
        
        result = await self.client.analyze_text(message)
        return {
            "sentiment": result.get("sentiment", {}),
            "patterns": result.get("patterns", {}),
            "feedback": None
        }
    
    async def generate_post_analysis(
        self,
        preparation_plan: Optional[Dict],
        actual_outcome: str,
        what_worked: Optional[str],
        what_didnt_work: Optional[str],
        emotions: Optional[str]
    ) -> Dict[str, Any]:
        """Generate post-conversation analysis"""
        
        if not self._ai_available or not self.client:
            return self._get_fallback_post_analysis()
        
        # Use generate endpoint for post analysis
        prompt = f"""Проанализируй результаты разговора:

Результат: {actual_outcome}
Что сработало: {what_worked or 'не указано'}
Что не сработало: {what_didnt_work or 'не указано'}
Эмоции: {emotions or 'не указано'}

Дай рекомендации для улучшения навыков общения."""

        response = await self.client.generate(prompt, max_tokens=1024)
        
        return {
            "plan_comparison": None,
            "success_factors": [],
            "improvement_areas": [],
            "lessons_learned": [],
            "recommendations_for_future": [response] if response else [],
            "skill_progress": {}
        }
    
    async def search_knowledge(
        self,
        query: str,
        topic: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        
        if not self._ai_available or not self.client:
            return []
        
        full_query = f"{topic} {query}" if topic else query
        results = await self.client.rag_search(full_query, top_k=limit)
        return results
    
    async def generate_chat_response(
        self,
        history: List[Dict[str, str]],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI response for general chat"""
        
        if not self._ai_available or not self.client:
            return {
                "message": "Привет! Я - AI-помощник для развития навыков общения. К сожалению, AI API временно недоступен. Пожалуйста, проверьте подключение к AI серверу.",
                "analysis": None,
                "suggestions": None
            }
        
        # Build prompt from history
        prompt_parts = []
        if context:
            prompt_parts.append(f"Контекст: {context}")
        
        for msg in history[-5:]:  # Last 5 messages
            role = "Пользователь" if msg["role"] == "user" else "Ассистент"
            prompt_parts.append(f"{role}: {msg['content']}")
        
        prompt = "\n".join(prompt_parts)
        
        response = await self.client.generate(
            prompt=prompt,
            max_tokens=1024,
            system_prompt="Ты - AI-помощник для развития навыков общения. Помогай пользователям улучшить их коммуникативные навыки."
        )
        
        return {
            "message": response,
            "analysis": None,
            "suggestions": None
        }
    
    # Fallback methods when AI is not available
    def _get_fallback_plan(self, conversation_type: str, situation: str) -> Dict:
        return {
            "situation_analysis": "AI API временно недоступен",
            "emotional_assessment": "Требуется подключение к AI серверу",
            "plan": [
                {
                    "phase": "Открытие",
                    "goals": ["Установить контакт", "Создать позитивную атмосферу"],
                    "key_phrases": ["Здравствуйте", "Спасибо за время"],
                    "techniques": ["Активное слушание"]
                },
                {
                    "phase": "Основная часть",
                    "goals": ["Изложить позицию", "Выслушать собеседника"],
                    "key_phrases": [],
                    "techniques": ["Я-сообщения"]
                },
                {
                    "phase": "Завершение",
                    "goals": ["Достичь договоренности", "Подвести итоги"],
                    "key_phrases": ["Давайте подведем итог"],
                    "techniques": ["Резюмирование"]
                }
            ],
            "scenarios": [],
            "objection_handling": [],
            "psychological_techniques": ["Активное слушание", "Эмпатия", "Я-сообщения"],
            "dos_and_donts": {
                "do": ["Слушайте внимательно", "Сохраняйте спокойствие"],
                "dont": ["Не перебивайте", "Не повышайте голос"]
            }
        }
    
    def _get_fallback_response(self, personality_type: str) -> Dict:
        return {
            "message": "AI API временно недоступен. Пожалуйста, проверьте подключение к AI серверу.",
            "user_message_analysis": None,
            "suggestions": None,
            "session_complete": False
        }
    
    def _get_fallback_analysis(self) -> Dict:
        return {
            "sentiment": {
                "overall": "neutral",
                "score": 0,
                "emotions": {},
                "tone": "neutral"
            },
            "patterns": [],
            "message_balance": {
                "i_messages_count": 0,
                "you_messages_count": 0,
                "i_messages_percentage": 0,
                "examples_i": [],
                "examples_you": [],
                "recommendation": "AI API недоступен"
            },
            "issues": [],
            "strengths": [],
            "recommendations": ["Подключитесь к AI серверу для полного анализа"],
            "alternatives": [],
            "overall_assessment": "Требуется подключение к AI серверу для анализа"
        }
    
    def _get_fallback_post_analysis(self) -> Dict:
        return {
            "plan_comparison": None,
            "success_factors": [],
            "improvement_areas": [],
            "lessons_learned": [],
            "recommendations_for_future": ["Подключитесь к AI серверу для анализа"],
            "skill_progress": {}
        }
