"""
LLM Client - Interface for model inference
Supports both custom model and external APIs
"""
import torch
from typing import Optional, Dict, Any, List
import asyncio
import json
import os

from config import config


class LLMClient:
    """
    Client for LLM operations
    Supports custom PyTorch model and external APIs (OpenAI, Anthropic)
    """
    
    def __init__(self, use_local: bool = True):
        self.use_local = use_local
        self.model = None
        self.tokenizer = None
        self.device = config.training.device if torch.cuda.is_available() else "cpu"
        
        if use_local:
            self._load_local_model()
        else:
            self._init_api_clients()
    
    def _load_local_model(self):
        """Load local PyTorch model"""
        try:
            from core.model import SocialSkillsModel
            from transformers import AutoTokenizer
            
            model_path = config.model.model_path
            
            if os.path.exists(model_path):
                # Load trained model
                self.model = SocialSkillsModel.from_pretrained(model_path, self.device)
                self.tokenizer = AutoTokenizer.from_pretrained(config.model.tokenizer_path)
            else:
                # Initialize new model
                print("No trained model found. Initializing new model...")
                self.model = SocialSkillsModel(
                    vocab_size=config.model.vocab_size,
                    hidden_size=config.model.hidden_size,
                    num_layers=config.model.num_layers,
                    num_heads=config.model.num_heads,
                    max_length=config.model.max_length
                ).to(self.device)
                
                # Use pre-trained tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "ai-forever/rugpt3small_based_on_gpt2"
                )
            
            self.model.eval()
            print(f"Model loaded on {self.device}")
            print(f"Parameters: {self.model.get_num_params():,}")
            
        except Exception as e:
            print(f"Error loading local model: {e}")
            self.use_local = False
            self._init_api_clients()
    
    def _init_api_clients(self):
        """Initialize API clients for external LLMs"""
        self.openai_client = None
        self.anthropic_client = None
        
        if config.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=config.openai_api_key)
            except:
                pass
        
        if config.anthropic_api_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=config.anthropic_api_key)
            except:
                pass
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text response"""
        
        if self.use_local and self.model is not None:
            return await self._generate_local(prompt, max_tokens, temperature)
        else:
            return await self._generate_api(prompt, max_tokens, temperature, system_prompt)
    
    async def _generate_local(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using local model"""
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=config.model.max_length - max_tokens
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=config.model.top_p,
                top_k=config.model.top_k,
                repetition_penalty=config.model.repetition_penalty,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        # Decode
        generated = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )
        
        return generated.strip()
    
    async def _generate_api(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Generate using external API"""
        
        if self.openai_client:
            return await self._generate_openai(prompt, max_tokens, temperature, system_prompt)
        elif self.anthropic_client:
            return await self._generate_anthropic(prompt, max_tokens, temperature, system_prompt)
        else:
            return "Error: No model available. Please train a local model or configure API keys."
    
    async def _generate_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Generate using OpenAI API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
        )
        
        return response.choices[0].message.content
    
    async def _generate_anthropic(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Generate using Anthropic API"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
        )
        
        return response.content[0].text
    
    # ===== Application-specific methods =====
    
    async def generate_conversation_plan(
        self,
        conversation_type: str,
        situation: str,
        interlocutor: Optional[str],
        desired_outcome: str,
        concerns: Optional[str],
        knowledge_context: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a conversation preparation plan"""
        
        context = ""
        if knowledge_context:
            context = "\n\nРелевантные знания из базы:\n"
            for item in knowledge_context[:3]:
                context += f"- {item.get('title', '')}: {item.get('content', '')[:200]}...\n"
        
        prompt = f"""Ты - эксперт по коммуникации и психологии общения. Помоги подготовиться к разговору.

Тип разговора: {conversation_type}
Ситуация: {situation}
Собеседник: {interlocutor or 'Не указан'}
Желаемый результат: {desired_outcome}
Опасения: {concerns or 'Не указаны'}
{context}

Создай детальный план подготовки к разговору в формате JSON:
{{
    "situation_analysis": "Анализ ситуации",
    "emotional_assessment": "Оценка эмоционального контекста",
    "plan": [
        {{
            "phase": "Открытие",
            "goals": ["цель1", "цель2"],
            "key_phrases": ["фраза1", "фраза2"],
            "techniques": ["техника1"],
            "warnings": ["предупреждение1"]
        }}
    ],
    "scenarios": [
        {{
            "condition": "Если собеседник...",
            "response_strategy": "Стратегия ответа",
            "key_phrases": ["фраза"]
        }}
    ],
    "objection_handling": [
        {{"objection": "Возражение", "response": "Ответ"}}
    ],
    "psychological_techniques": ["техника1", "техника2"],
    "dos_and_donts": {{
        "do": ["Делайте"],
        "dont": ["Не делайте"]
    }}
}}"""

        response = await self.generate(prompt, max_tokens=2000, temperature=0.7)
        
        try:
            # Try to parse JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            pass
        
        # Return default structure if parsing fails
        return {
            "situation_analysis": response[:500],
            "emotional_assessment": "Анализ в процессе",
            "plan": [],
            "scenarios": [],
            "objection_handling": [],
            "psychological_techniques": [],
            "dos_and_donts": {"do": [], "dont": []}
        }
    
    async def generate_dialogue_response(
        self,
        personality_type: str,
        scenario: str,
        history: List[Dict[str, str]],
        user_analysis: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate AI response in dialogue simulation"""
        
        personality_descriptions = {
            "assertive": "уверенный, прямой, отстаивает свою позицию",
            "passive": "уступчивый, избегает конфликтов, соглашается",
            "aggressive": "напористый, может перебивать, давит",
            "passive_aggressive": "саркастичный, непрямой, манипулятивный",
            "manipulative": "использует манипуляции, давление, чувство вины",
            "supportive": "поддерживающий, эмпатичный, слушающий",
            "skeptical": "сомневающийся, задает много вопросов"
        }
        
        personality_desc = personality_descriptions.get(personality_type, "нейтральный")
        
        history_text = "\n".join([
            f"{'Пользователь' if m['role'] == 'user' else 'Собеседник'}: {m['content']}"
            for m in history[-10:]  # Last 10 messages
        ])
        
        prompt = f"""Ты играешь роль собеседника в тренировочном диалоге.

Сценарий: {scenario}
Твой тип личности: {personality_type} ({personality_desc})

История диалога:
{history_text}

Ответь как этот собеседник. Будь реалистичным и последовательным в своей роли.
После ответа, дай 1-2 коротких совета пользователю (в скобках).

Формат:
[Твой ответ как собеседника]

(Советы: ...)"""

        response = await self.generate(prompt, max_tokens=500, temperature=0.8)
        
        # Parse response and suggestions
        suggestions = []
        message = response
        
        if "(Советы:" in response or "(Совет:" in response:
            parts = response.split("(Совет")
            message = parts[0].strip()
            if len(parts) > 1:
                suggestion_text = parts[1].replace("ы:", "").replace(":", "").strip().rstrip(")")
                suggestions = [s.strip() for s in suggestion_text.split(",")]
        
        return {
            "message": message,
            "suggestions": suggestions,
            "session_complete": False
        }
    
    async def generate_recommendations(
        self,
        text: str,
        context: Optional[str],
        sentiment: Dict,
        patterns: List,
        issues: List
    ) -> Dict[str, Any]:
        """Generate recommendations for text improvement"""
        
        prompt = f"""Проанализируй этот текст переписки и дай рекомендации:

Текст: {text[:2000]}
Контекст: {context or 'Не указан'}
Sentiment: {sentiment.get('overall', 'neutral')}
Выявленные паттерны: {', '.join([p.get('pattern_type', '') for p in patterns[:5]])}
Проблемы: {', '.join([i.get('issue_type', '') for i in issues[:5]])}

Дай рекомендации в формате JSON:
{{
    "strengths": ["сильная сторона 1", "сильная сторона 2"],
    "recommendations": ["рекомендация 1", "рекомендация 2"],
    "alternatives": [
        {{
            "original": "исходная фраза",
            "alternatives": ["вариант 1", "вариант 2"],
            "explanation": "почему лучше"
        }}
    ],
    "overall_assessment": "Общая оценка коммуникации"
}}"""

        response = await self.generate(prompt, max_tokens=1500, temperature=0.7)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            pass
        
        return {
            "strengths": [],
            "recommendations": [response[:500]],
            "alternatives": [],
            "overall_assessment": "Требуется дополнительный анализ"
        }
    
    async def generate_quick_feedback(self, message: str) -> str:
        """Generate quick feedback on user's message in dialogue"""
        
        prompt = f"""Кратко оцени эту реплику в диалоге (1-2 предложения):
"{message}"

Что хорошо и что можно улучшить?"""

        return await self.generate(prompt, max_tokens=100, temperature=0.7)
    
    async def generate_post_analysis(
        self,
        preparation_plan: Optional[Dict],
        actual_outcome: str,
        what_worked: Optional[str],
        what_didnt_work: Optional[str],
        emotions: Optional[str]
    ) -> Dict[str, Any]:
        """Generate post-conversation analysis"""
        
        plan_summary = ""
        if preparation_plan:
            plan_summary = f"План разговора: {json.dumps(preparation_plan, ensure_ascii=False)[:500]}"
        
        prompt = f"""Проанализируй результаты разговора:

{plan_summary}
Фактический результат: {actual_outcome}
Что сработало: {what_worked or 'Не указано'}
Что не сработало: {what_didnt_work or 'Не указано'}
Эмоции: {emotions or 'Не указаны'}

Дай анализ в формате JSON:
{{
    "plan_comparison": {{"следование_плану": "описание", "отклонения": "описание"}},
    "success_factors": ["фактор 1", "фактор 2"],
    "improvement_areas": ["область 1", "область 2"],
    "lessons_learned": ["урок 1", "урок 2"],
    "recommendations_for_future": ["рекомендация 1"],
    "skill_progress": {{"навык": "изменение"}}
}}"""

        response = await self.generate(prompt, max_tokens=1000, temperature=0.7)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            pass
        
        return {
            "success_factors": [],
            "improvement_areas": [],
            "lessons_learned": [response[:300]],
            "recommendations_for_future": [],
            "skill_progress": {}
        }
    
    async def generate_reflection_insights(
        self,
        content: str,
        mood: int
    ) -> Dict[str, str]:
        """Generate insights for reflection entry"""
        
        mood_desc = "плохое" if mood < 4 else "нормальное" if mood < 7 else "хорошее"
        
        prompt = f"""Пользователь записал рефлексию (настроение: {mood}/10 - {mood_desc}):

"{content[:1000]}"

Дай краткий инсайт или поддерживающий комментарий (2-3 предложения):"""

        insights = await self.generate(prompt, max_tokens=150, temperature=0.7)
        
        return {"insights": insights}
