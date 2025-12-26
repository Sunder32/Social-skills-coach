"""
AI API Client - HTTP client for external AI API
Connects to remote AI API Server
"""
import httpx
from typing import Dict, List, Any, Optional
import os
import json
from app.config import settings


class AIAPIClient:
    """
    HTTP Client for external AI API.
    Uses simple /chat endpoint for all AI operations.
    """
    
    def __init__(self):
        self.base_url = settings.AI_API_URL
        self.api_key = settings.AI_API_KEY
        self.timeout = settings.AI_API_TIMEOUT
        
        headers = {"Content-Type": "application/json"}
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
            response = await self.client.get("/")
            response.raise_for_status()
            return {
                "status": "available",
                "details": response.json()
            }
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
        """Generate text response using /chat endpoint"""
        try:
            message = prompt
            if system_prompt:
                message = f"{system_prompt}\n\n{prompt}"
            
            print(f"[AI] Sending request to {self.base_url}/chat")
            response = await self.client.post("/chat", json={
                "message": message,
                "max_tokens": max_tokens,
                "temperature": temperature
            })
            print(f"[AI] Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            return data.get("response", data.get("text", ""))
        except httpx.ConnectError as e:
            error_msg = f"Не удалось подключиться к AI серверу. Проверьте интернет-соединение."
            print(f"AI API connection error: {e}")
            return f"[AI Error: {error_msg}]"
        except httpx.TimeoutException as e:
            error_msg = f"Превышено время ожидания ответа от AI сервера. Попробуйте позже."
            print(f"AI API timeout error: {e}")
            return f"[AI Error: {error_msg}]"
        except Exception as e:
            print(f"AI API generate error: {type(e).__name__}: {e}")
            return f"[AI Error: {str(e)}]"
    
    async def chat_with_file(
        self,
        file_content: bytes,
        file_name: str,
        message: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """Send file with message using /chat/file endpoint"""
        try:
            files = {"file": (file_name, file_content)}
            data = {
                "message": message,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = await self.client.post("/chat/file", files=files, data=data)
            response.raise_for_status()
            result = response.json()
            return result.get("response", result.get("text", ""))
        except Exception as e:
            print(f"AI API chat with file error: {e}")
            return f"[AI Error: {str(e)}]"
    
    async def chat_with_file_base64(
        self,
        file_content_base64: str,
        file_name: str,
        message: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """Send base64 encoded file with message using /chat/file/base64 endpoint"""
        try:
            response = await self.client.post("/chat/file/base64", json={
                "message": message,
                "file_content": file_content_base64,
                "file_name": file_name,
                "max_tokens": max_tokens,
                "temperature": temperature
            })
            response.raise_for_status()
            data = response.json()
            return data.get("response", data.get("text", ""))
        except Exception as e:
            print(f"AI API chat with base64 file error: {e}")
            return f"[AI Error: {str(e)}]"
    
    async def analyze_text_endpoint(
        self,
        text: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """Analyze text using /analyze/text endpoint"""
        try:
            response = await self.client.post("/analyze/text", json={
                "message": text,
                "max_tokens": max_tokens,
                "temperature": temperature
            })
            response.raise_for_status()
            data = response.json()
            return data.get("response", data.get("text", ""))
        except Exception as e:
            print(f"AI API analyze text error: {e}")
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
        """Generate a conversation preparation plan using /chat endpoint"""
        try:
            prompt = f"""Создай детальный план подготовки к разговору.

Тип разговора: {conversation_type}
Ситуация: {situation}
Собеседник: {interlocutor or 'Не указан'}
Желаемый результат: {desired_outcome}
Опасения: {concerns or 'Нет'}

Предоставь структурированный план в формате JSON с полями:
- situation_analysis: анализ ситуации
- emotional_assessment: оценка эмоционального состояния
- plan: список шагов для подготовки
- scenarios: возможные сценарии развития
- objection_handling: как работать с возражениями
- psychological_techniques: психологические техники
- dos_and_donts: что делать и чего избегать"""

            response_text = await self.generate(prompt, max_tokens=2000, temperature=0.7)
            
            # Попытка распарсить JSON из ответа
            try:
                return json.loads(response_text)
            except:
                # Если не JSON, возвращаем структурированный fallback с текстом
                return {
                    "situation_analysis": response_text[:200],
                    "emotional_assessment": "Анализ получен от AI",
                    "plan": response_text.split('\n')[:5],
                    "scenarios": [],
                    "objection_handling": [],
                    "psychological_techniques": ["Активное слушание", "Эмпатия"],
                    "dos_and_donts": {"dos": [], "donts": []}
                }
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
        """Generate AI response in dialogue simulation using /chat endpoint"""
        try:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]])
            
            prompt = f"""Ты симулируешь собеседника с типом личности: {personality_type}
Сценарий: {scenario}

История диалога:
{history_text}

Ответь в роли этого персонажа. Дай только ответ персонажа, без пояснений."""

            response_text = await self.generate(prompt, max_tokens=500, temperature=0.8)
            
            return {
                "message": response_text,
                "suggestions": ["Попробуйте использовать я-высказывания"],
                "session_complete": False
            }
        except Exception as e:
            print(f"AI API dialogue error: {e}")
            return self._get_fallback_response(personality_type)
    
    async def analyze_text(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze text for communication patterns using /chat endpoint"""
        try:
            prompt = f"""Проанализируй следующий текст сообщения на предмет коммуникационных паттернов.
            
Текст: {text}
{f'Контекст: {context}' if context else ''}

Предоставь анализ в формате JSON с полями:
- sentiment: {{"polarity": float, "subjectivity": float}}
- patterns: список найденных паттернов
- message_balance: {{"i_messages": int, "you_messages": int}}
- issues: список проблем в коммуникации
- recommendations: список рекомендаций"""

            response_text = await self.generate(prompt, max_tokens=1500, temperature=0.5)
            
            # Попытка распарсить JSON
            try:
                return json.loads(response_text)
            except:
                # Fallback с текстовым анализом
                return {
                    "sentiment": {"polarity": 0, "subjectivity": 0.5},
                    "patterns": {"analysis": response_text[:300]},
                    "message_balance": {"i_messages": 0, "you_messages": 0},
                    "issues": [],
                    "recommendations": [response_text[:200]]
                }
        except Exception as e:
            print(f"AI API analyze error: {e}")
            return self._get_fallback_analysis()
    
    async def rag_search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base - not available in simple chat API"""
        print(f"RAG search not available in simple chat API")
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
