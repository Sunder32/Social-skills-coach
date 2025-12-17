"""
Sentiment Analysis
Analyzes emotional tone in text
"""
from typing import Dict, List, Optional, Tuple
import re

# Simple rule-based sentiment for Russian text
# In production, use transformer model

POSITIVE_WORDS = {
    "хорошо", "отлично", "прекрасно", "замечательно", "здорово",
    "рад", "рада", "счастлив", "доволен", "довольна", "спасибо",
    "благодарю", "люблю", "нравится", "понравилось", "успех",
    "победа", "удача", "молодец", "супер", "класс", "круто",
    "интересно", "красиво", "приятно", "весело", "улыбка"
}

NEGATIVE_WORDS = {
    "плохо", "ужасно", "отвратительно", "кошмар", "провал",
    "злюсь", "злой", "злая", "ненавижу", "раздражает", "бесит",
    "грустно", "печально", "обидно", "разочарован", "разочарована",
    "неудача", "проблема", "ошибка", "тяжело", "сложно", "трудно",
    "страшно", "боюсь", "тревожно", "беспокоюсь", "устал", "устала"
}

EMOTION_PATTERNS = {
    "радость": ["рад", "счастлив", "доволен", "отлично", "ура", "класс"],
    "грусть": ["грустно", "печально", "тоскливо", "одиноко", "скучаю"],
    "злость": ["злюсь", "бесит", "раздражает", "ненавижу", "достало"],
    "страх": ["боюсь", "страшно", "тревожно", "волнуюсь", "беспокоюсь"],
    "удивление": ["вау", "ого", "неожиданно", "странно", "удивлен"],
    "интерес": ["интересно", "любопытно", "хочу узнать", "расскажи"]
}


class SentimentAnalyzer:
    """
    Analyzes sentiment and emotions in text
    """
    
    def __init__(self):
        self.positive_words = POSITIVE_WORDS
        self.negative_words = NEGATIVE_WORDS
        self.emotion_patterns = EMOTION_PATTERNS
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment analysis results
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Count sentiment words
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        
        # Calculate scores
        total = pos_count + neg_count
        if total == 0:
            sentiment_score = 0.0
            sentiment = "neutral"
        else:
            sentiment_score = (pos_count - neg_count) / total
            if sentiment_score > 0.2:
                sentiment = "positive"
            elif sentiment_score < -0.2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        
        # Detect emotions
        emotions = self._detect_emotions(text_lower)
        
        # Check intensity markers
        intensity = self._check_intensity(text)
        
        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "positive_count": pos_count,
            "negative_count": neg_count,
            "emotions": emotions,
            "intensity": intensity,
            "confidence": min(0.3 + total * 0.1, 0.9)  # Simple confidence
        }
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect specific emotions"""
        emotions = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = sum(1 for p in patterns if p in text)
            if score > 0:
                emotions[emotion] = min(score * 0.3, 1.0)
        
        return emotions
    
    def _check_intensity(self, text: str) -> str:
        """Check emotional intensity"""
        # Exclamation marks
        exclaim_count = text.count('!')
        
        # Caps ratio
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        # Repeated characters (e.g., "ооочень")
        repeated = bool(re.search(r'(.)\1{2,}', text))
        
        if exclaim_count > 2 or caps_ratio > 0.5 or repeated:
            return "high"
        elif exclaim_count > 0:
            return "medium"
        else:
            return "low"
    
    def analyze_conversation(
        self,
        messages: List[Dict]
    ) -> Dict:
        """
        Analyze sentiment dynamics in conversation
        
        Args:
            messages: List of messages with 'content' and 'role'
            
        Returns:
            Conversation sentiment analysis
        """
        if not messages:
            return {"average_sentiment": 0, "trend": "neutral", "messages": []}
        
        user_messages = [m for m in messages if m.get("role") == "user"]
        
        analyses = []
        scores = []
        
        for msg in user_messages:
            analysis = self.analyze(msg.get("content", ""))
            analyses.append(analysis)
            scores.append(analysis["sentiment_score"])
        
        # Calculate trend
        if len(scores) >= 2:
            first_half = sum(scores[:len(scores)//2]) / max(len(scores)//2, 1)
            second_half = sum(scores[len(scores)//2:]) / max(len(scores) - len(scores)//2, 1)
            
            diff = second_half - first_half
            if diff > 0.2:
                trend = "improving"
            elif diff < -0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "average_sentiment": sum(scores) / len(scores) if scores else 0,
            "trend": trend,
            "message_count": len(analyses),
            "messages": analyses
        }
