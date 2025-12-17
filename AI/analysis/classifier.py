"""
Communication Style Classifier
Classifies communication into types and scenarios
"""
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum


class CommunicationStyle(Enum):
    """Communication styles"""
    ASSERTIVE = "assertive"  # Уверенный
    AGGRESSIVE = "aggressive"  # Агрессивный
    PASSIVE = "passive"  # Пассивный
    PASSIVE_AGGRESSIVE = "passive_aggressive"  # Пассивно-агрессивный
    MANIPULATIVE = "manipulative"  # Манипулятивный


class ConversationType(Enum):
    """Types of conversations"""
    SMALL_TALK = "small_talk"  # Светская беседа
    CONFLICT = "conflict"  # Конфликт
    NEGOTIATION = "negotiation"  # Переговоры
    EMOTIONAL_SUPPORT = "emotional_support"  # Эмоциональная поддержка
    FEEDBACK = "feedback"  # Обратная связь
    REQUEST = "request"  # Просьба
    REFUSAL = "refusal"  # Отказ


# Style indicators
STYLE_INDICATORS = {
    CommunicationStyle.ASSERTIVE: {
        "positive": ["я думаю", "я хотел бы", "мне важно", "я предлагаю", "давай обсудим"],
        "weight": 1.0
    },
    CommunicationStyle.AGGRESSIVE: {
        "positive": ["ты должен", "почему ты", "из-за тебя", "ты всегда", "хватит"],
        "weight": 1.0
    },
    CommunicationStyle.PASSIVE: {
        "positive": ["не знаю", "наверное", "может быть", "как скажешь", "мне всё равно"],
        "weight": 1.0
    },
    CommunicationStyle.PASSIVE_AGGRESSIVE: {
        "positive": ["конечно, конечно", "как хочешь", "ну ладно", "делай что хочешь"],
        "weight": 1.0
    },
    CommunicationStyle.MANIPULATIVE: {
        "positive": ["если ты меня любишь", "все нормальные люди", "ты же не хочешь"],
        "weight": 1.0
    }
}

# Conversation type indicators
TYPE_INDICATORS = {
    ConversationType.SMALL_TALK: {
        "keywords": ["как дела", "погода", "что нового", "выходные", "праздник"],
        "weight": 1.0
    },
    ConversationType.CONFLICT: {
        "keywords": ["не согласен", "проблема", "конфликт", "спор", "недоволен"],
        "weight": 1.0
    },
    ConversationType.NEGOTIATION: {
        "keywords": ["условия", "предложение", "согласовать", "договориться", "компромисс"],
        "weight": 1.0
    },
    ConversationType.EMOTIONAL_SUPPORT: {
        "keywords": ["грустно", "переживаю", "поддержи", "тяжело", "помоги пережить"],
        "weight": 1.0
    },
    ConversationType.FEEDBACK: {
        "keywords": ["обратная связь", "отзыв", "оценка", "что думаешь", "как тебе"],
        "weight": 1.0
    },
    ConversationType.REQUEST: {
        "keywords": ["просьба", "можешь ли", "не мог бы", "помоги", "нужна помощь"],
        "weight": 1.0
    },
    ConversationType.REFUSAL: {
        "keywords": ["не могу", "откажусь", "не получится", "нет возможности"],
        "weight": 1.0
    }
}


class CommunicationClassifier:
    """
    Classifies communication style and conversation type
    """
    
    def __init__(self):
        self.style_indicators = STYLE_INDICATORS
        self.type_indicators = TYPE_INDICATORS
    
    def classify_style(self, text: str) -> Dict:
        """
        Classify communication style
        
        Args:
            text: Text to classify
            
        Returns:
            Style classification results
        """
        text_lower = text.lower()
        
        scores = {}
        max_score = 0
        dominant_style = None
        
        for style, config in self.style_indicators.items():
            score = 0
            matches = []
            
            for indicator in config["positive"]:
                if indicator in text_lower:
                    score += config["weight"]
                    matches.append(indicator)
            
            scores[style.value] = {
                "score": score,
                "matches": matches
            }
            
            if score > max_score:
                max_score = score
                dominant_style = style.value
        
        return {
            "dominant_style": dominant_style or CommunicationStyle.ASSERTIVE.value,
            "confidence": min(max_score * 0.3, 0.9) if max_score > 0 else 0.3,
            "scores": scores
        }
    
    def classify_conversation_type(self, text: str) -> Dict:
        """
        Classify conversation type
        
        Args:
            text: Text to classify
            
        Returns:
            Type classification results
        """
        text_lower = text.lower()
        
        scores = {}
        max_score = 0
        dominant_type = None
        
        for conv_type, config in self.type_indicators.items():
            score = 0
            matches = []
            
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += config["weight"]
                    matches.append(keyword)
            
            scores[conv_type.value] = {
                "score": score,
                "matches": matches
            }
            
            if score > max_score:
                max_score = score
                dominant_type = conv_type.value
        
        return {
            "dominant_type": dominant_type or ConversationType.SMALL_TALK.value,
            "confidence": min(max_score * 0.3, 0.9) if max_score > 0 else 0.3,
            "scores": scores
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Full classification analysis
        
        Args:
            text: Text to analyze
            
        Returns:
            Complete classification results
        """
        style = self.classify_style(text)
        conv_type = self.classify_conversation_type(text)
        
        # Get recommendations based on style
        recommendations = self._get_recommendations(style["dominant_style"])
        
        return {
            "style": style,
            "conversation_type": conv_type,
            "recommendations": recommendations
        }
    
    def _get_recommendations(self, style: str) -> List[str]:
        """Get recommendations based on style"""
        recommendations = {
            CommunicationStyle.ASSERTIVE.value: [
                "Продолжайте в том же духе!",
                "Ваш стиль общения конструктивен"
            ],
            CommunicationStyle.AGGRESSIVE.value: [
                "Попробуйте использовать 'я-высказывания' вместо обвинений",
                "Сделайте паузу перед ответом, чтобы успокоиться",
                "Фокусируйтесь на проблеме, а не на человеке"
            ],
            CommunicationStyle.PASSIVE.value: [
                "Выражайте своё мнение более уверенно",
                "Ваши потребности тоже важны - не бойтесь о них говорить",
                "Практикуйте чёткие 'я-высказывания'"
            ],
            CommunicationStyle.PASSIVE_AGGRESSIVE.value: [
                "Выражайте свои чувства прямо, без намёков",
                "Если вас что-то беспокоит - скажите об этом открыто",
                "Прямая коммуникация эффективнее скрытой агрессии"
            ],
            CommunicationStyle.MANIPULATIVE.value: [
                "Попробуйте выражать свои потребности напрямую",
                "Уважайте право собеседника на собственное решение",
                "Стройте отношения на доверии, а не на манипуляциях"
            ]
        }
        
        return recommendations.get(style, [])
    
    def analyze_conversation(
        self,
        messages: List[Dict]
    ) -> Dict:
        """
        Analyze full conversation
        
        Args:
            messages: List of messages with 'content' and 'role'
            
        Returns:
            Conversation classification analysis
        """
        user_messages = [m for m in messages if m.get("role") == "user"]
        
        if not user_messages:
            return {
                "dominant_style": CommunicationStyle.ASSERTIVE.value,
                "style_distribution": {},
                "conversation_type": ConversationType.SMALL_TALK.value,
                "recommendations": []
            }
        
        # Combine all user text
        combined_text = " ".join(m.get("content", "") for m in user_messages)
        
        # Classify
        analysis = self.analyze(combined_text)
        
        # Get style distribution across messages
        style_counts = {}
        for msg in user_messages:
            result = self.classify_style(msg.get("content", ""))
            style = result["dominant_style"]
            style_counts[style] = style_counts.get(style, 0) + 1
        
        total = len(user_messages)
        style_distribution = {
            k: v / total for k, v in style_counts.items()
        }
        
        return {
            "dominant_style": analysis["style"]["dominant_style"],
            "style_distribution": style_distribution,
            "conversation_type": analysis["conversation_type"]["dominant_type"],
            "recommendations": analysis["recommendations"],
            "message_count": total
        }
