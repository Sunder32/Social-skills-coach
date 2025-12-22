"""
AI API Client - HTTP client for external AI API
Connects to DASA AI API Server
"""
import httpx
from typing import Dict, List, Any, Optional
import os


class AIAPIClient:
    """
    HTTP Client for external AI API.
    Replaces local AI module with API calls to DASA server.
    """
    
    def __init__(self):
        self.base_url = os.environ.get("AI_API_URL", "http://localhost:8100/api/v1")
        self.api_key = os.environ.get("AI_API_KEY", "")
        self.timeout = float(os.environ.get("AI_API_TIMEOUT", "60"))
        
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout
        )
        
        print(f"AI API Client initialized: {self.base_url}")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if AI API is available"""
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "unavailable",
                "error": str(e)
            }
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text response"""
        try:
            response = await self.client.post("/generate", json={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system_prompt": system_prompt
            })
            response.raise_for_status()
            return response.json().get("text", "")
        except Exception as e:
            print(f"AI API generate error: {e}")
            return f"[AI Error: {str(e)}]"
    
    async def generate_conversation_plan(
        self,
        conversation_type: str,
        situation: str,
        interlocutor: Optional[str],
        desired_outcome: str,
        concerns: Optional[str],
        knowledge_context: List[Any] = None
    ) -> Dict[str, Any]:
        """Generate a conversation preparation plan"""
        try:
            response = await self.client.post("/conversation/plan", json={
                "conversation_type": conversation_type,
                "situation": situation,
                "interlocutor": interlocutor,
                "desired_outcome": desired_outcome,
                "concerns": concerns
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"AI API plan error: {e}")
            return self._get_fallback_plan(conversation_type, situation)
    
    async def generate_dialogue_response(
        self,
        personality_type: str,
        scenario: str,
        history: List[Dict[str, str]],
        user_analysis: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate AI response in dialogue simulation"""
        try:
            response = await self.client.post("/dialogue/respond", json={
                "personality_type": personality_type,
                "scenario": scenario,
                "history": history
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"AI API dialogue error: {e}")
            return self._get_fallback_response(personality_type)
    
    async def analyze_text(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze text for communication patterns"""
        try:
            response = await self.client.post("/analyze", json={
                "text": text,
                "context": context
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"AI API analyze error: {e}")
            return self._get_fallback_analysis()
    
    async def rag_search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base using RAG"""
        try:
            response = await self.client.post("/rag/search", json={
                "query": query,
                "top_k": top_k
            })
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"AI API RAG search error: {e}")
            return []
    
    async def generate_recommendations(
        self,
        text: str,
        context: Optional[str],
        sentiment: Dict,
        patterns: Dict,
        issues: List
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        # Use the analyze endpoint which includes recommendations
        analysis = await self.analyze_text(text, context)
        return analysis.get("recommendations", [])
    
    # Fallback methods for when API is unavailable
    
    def _get_fallback_plan(self, conversation_type: str, situation: str) -> Dict[str, Any]:
        """Fallback plan when API is unavailable"""
        return {
            "situation_analysis": f"Анализ ситуации: {situation}",
            "emotional_assessment": "Рекомендуется сохранять спокойствие и уверенность",
            "plan": [
                "Подготовьтесь к разговору заранее",
                "Определите свои цели и границы",
                "Выслушайте собеседника",
                "Выразите свою позицию ясно и уважительно",
                "Стремитесь к взаимовыгодному решению"
            ],
            "scenarios": [],
            "objection_handling": [],
            "psychological_techniques": [
                "Активное слушание",
                "Я-высказывания",
                "Эмпатия"
            ],
            "dos_and_donts": {
                "dos": ["Слушайте", "Будьте открыты", "Сохраняйте спокойствие"],
                "donts": ["Не перебивайте", "Не переходите на личности", "Не повышайте голос"]
            }
        }
    
    def _get_fallback_response(self, personality_type: str) -> Dict[str, Any]:
        """Fallback response when API is unavailable"""
        responses = {
            "assertive": "Понимаю вашу точку зрения. Давайте обсудим это подробнее.",
            "passive": "Хорошо, как скажете...",
            "aggressive": "Это неприемлемо! Нужно решить это сейчас же!",
            "passive_aggressive": "Ну ладно, если вы так считаете... хотя я бы сделал иначе."
        }
        return {
            "message": responses.get(personality_type, "Продолжим наш разговор."),
            "suggestions": ["Попробуйте использовать я-высказывания"],
            "session_complete": False
        }
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when API is unavailable"""
        return {
            "sentiment": {"polarity": 0, "subjectivity": 0.5},
            "patterns": {},
            "message_balance": {"i_messages": 0, "you_messages": 0},
            "issues": [],
            "recommendations": ["AI анализ временно недоступен"]
        }
