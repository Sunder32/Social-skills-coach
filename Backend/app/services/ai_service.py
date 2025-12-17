"""
AI Service - integrates with AI module for all AI operations
"""
import sys
import os
from typing import Dict, List, Any, Optional

# Add AI module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'AI'))

from app.config import settings


class AIService:
    """
    Service for AI operations
    Integrates Backend with AI module
    """
    
    def __init__(self):
        self._initialize_ai_modules()
    
    def _initialize_ai_modules(self):
        """Initialize AI module components"""
        try:
            from core.llm_client import LLMClient
            from rag.retriever import RAGRetriever
            from analysis.sentiment import SentimentAnalyzer
            from analysis.patterns import PatternAnalyzer
            
            self.llm_client = LLMClient()
            self.rag_retriever = RAGRetriever()
            self.sentiment_analyzer = SentimentAnalyzer()
            self.pattern_analyzer = PatternAnalyzer()
            self._ai_available = True
        except ImportError as e:
            print(f"Warning: AI modules not fully available: {e}")
            self._ai_available = False
            self.llm_client = None
            self.rag_retriever = None
            self.sentiment_analyzer = None
            self.pattern_analyzer = None
    
    async def generate_conversation_plan(
        self,
        conversation_type: str,
        situation: str,
        interlocutor: Optional[str],
        desired_outcome: str,
        concerns: Optional[str]
    ) -> Dict[str, Any]:
        """Generate a conversation preparation plan"""
        
        if not self._ai_available:
            return self._get_fallback_plan(conversation_type, situation)
        
        # Search knowledge base for relevant techniques
        relevant_knowledge = await self.rag_retriever.search(
            query=f"{conversation_type} {situation}",
            top_k=5
        )
        
        # Generate plan using LLM
        plan = await self.llm_client.generate_conversation_plan(
            conversation_type=conversation_type,
            situation=situation,
            interlocutor=interlocutor,
            desired_outcome=desired_outcome,
            concerns=concerns,
            knowledge_context=relevant_knowledge
        )
        
        return plan
    
    async def generate_dialogue_response(
        self,
        personality_type: str,
        scenario: str,
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate AI response in dialogue simulation"""
        
        if not self._ai_available:
            return self._get_fallback_response(personality_type)
        
        # Analyze last user message if exists
        user_message_analysis = None
        if history and history[-1]["role"] == "user":
            user_message_analysis = await self.analyze_user_message(
                history[-1]["content"]
            )
        
        # Generate response
        response = await self.llm_client.generate_dialogue_response(
            personality_type=personality_type,
            scenario=scenario,
            history=history,
            user_analysis=user_message_analysis
        )
        
        return {
            "message": response["message"],
            "user_message_analysis": user_message_analysis,
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
        
        if not self._ai_available:
            return self._get_fallback_analysis()
        
        # Sentiment analysis
        sentiment = await self.sentiment_analyzer.analyze(text)
        
        # Pattern analysis
        patterns = await self.pattern_analyzer.analyze(text)
        
        # I-messages vs You-messages
        message_balance = await self.pattern_analyzer.analyze_message_balance(text)
        
        # Detect issues
        issues = await self.pattern_analyzer.detect_issues(text)
        
        # Get recommendations from LLM
        recommendations = await self.llm_client.generate_recommendations(
            text=text,
            context=context,
            sentiment=sentiment,
            patterns=patterns,
            issues=issues
        )
        
        return {
            "sentiment": sentiment,
            "patterns": patterns,
            "message_balance": message_balance,
            "issues": issues,
            "strengths": recommendations.get("strengths", []),
            "recommendations": recommendations.get("recommendations", []),
            "alternatives": recommendations.get("alternatives", []),
            "overall_assessment": recommendations.get("overall_assessment", "")
        }
    
    async def analyze_user_message(self, message: str) -> Dict[str, Any]:
        """Quick analysis of user's message in dialogue"""
        
        if not self._ai_available:
            return {}
        
        sentiment = await self.sentiment_analyzer.analyze(message)
        patterns = await self.pattern_analyzer.quick_analyze(message)
        
        return {
            "sentiment": sentiment,
            "patterns": patterns,
            "feedback": await self.llm_client.generate_quick_feedback(message)
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
        
        if not self._ai_available:
            return self._get_fallback_post_analysis()
        
        return await self.llm_client.generate_post_analysis(
            preparation_plan=preparation_plan,
            actual_outcome=actual_outcome,
            what_worked=what_worked,
            what_didnt_work=what_didnt_work,
            emotions=emotions
        )
    
    async def search_knowledge(
        self,
        query: str,
        topic: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        
        if not self._ai_available or not self.rag_retriever:
            return []
        
        return await self.rag_retriever.search(
            query=query,
            topic=topic,
            top_k=limit
        )
    
    # Fallback methods when AI is not available
    def _get_fallback_plan(self, conversation_type: str, situation: str) -> Dict:
        return {
            "situation_analysis": "AI анализ временно недоступен",
            "emotional_assessment": "Требуется подключение AI модуля",
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
            "message": "AI модуль временно недоступен. Пожалуйста, попробуйте позже.",
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
                "recommendation": "AI анализ недоступен"
            },
            "issues": [],
            "strengths": [],
            "recommendations": ["Подключите AI модуль для полного анализа"],
            "alternatives": [],
            "overall_assessment": "Требуется подключение AI модуля для анализа"
        }
    
    def _get_fallback_post_analysis(self) -> Dict:
        return {
            "plan_comparison": None,
            "success_factors": [],
            "improvement_areas": [],
            "lessons_learned": [],
            "recommendations_for_future": ["Подключите AI модуль для анализа"],
            "skill_progress": {}
        }
