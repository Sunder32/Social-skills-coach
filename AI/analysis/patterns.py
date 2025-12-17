"""
Communication Pattern Detector
Detects patterns and issues in communication
"""
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass


@dataclass
class Pattern:
    """Detected communication pattern"""
    name: str
    category: str  # positive, negative, neutral
    description: str
    examples: List[str]
    suggestion: Optional[str] = None


# Communication patterns to detect
PATTERNS = {
    # Negative patterns
    "aggressive_language": Pattern(
        name="Агрессивная речь",
        category="negative",
        description="Использование агрессивных или обвинительных конструкций",
        examples=["ты всегда", "ты никогда", "из-за тебя", "это твоя вина"],
        suggestion="Попробуйте использовать 'Я-высказывания' вместо обвинений"
    ),
    "interruption_markers": Pattern(
        name="Перебивание",
        category="negative",
        description="Признаки перебивания собеседника",
        examples=["подожди", "дай сказать", "не перебивай"],
        suggestion="Дайте собеседнику закончить мысль перед ответом"
    ),
    "passive_aggressive": Pattern(
        name="Пассивная агрессия",
        category="negative",
        description="Скрытая агрессия через сарказм или намёки",
        examples=["как хочешь", "мне всё равно", "делай как знаешь", "ну конечно"],
        suggestion="Выражайте свои чувства и потребности прямо"
    ),
    "generalizations": Pattern(
        name="Обобщения",
        category="negative",
        description="Чрезмерное обобщение ситуаций",
        examples=["всегда", "никогда", "все", "никто", "постоянно"],
        suggestion="Говорите о конкретных ситуациях, избегая обобщений"
    ),
    "dismissive": Pattern(
        name="Обесценивание",
        category="negative",
        description="Отвержение чувств или мнения собеседника",
        examples=["это ерунда", "не выдумывай", "ты преувеличиваешь", "не драматизируй"],
        suggestion="Признайте право собеседника на его чувства"
    ),
    
    # Positive patterns
    "active_listening": Pattern(
        name="Активное слушание",
        category="positive",
        description="Признаки внимательного слушания",
        examples=["я понимаю", "правильно ли я понял", "то есть ты говоришь"],
        suggestion=None
    ),
    "empathy": Pattern(
        name="Эмпатия",
        category="positive",
        description="Проявление понимания чувств других",
        examples=["я понимаю как тебе", "это действительно", "мне жаль что"],
        suggestion=None
    ),
    "i_statements": Pattern(
        name="Я-высказывания",
        category="positive",
        description="Выражение своих чувств через 'я'",
        examples=["я чувствую", "мне кажется", "я думаю", "я хотел бы"],
        suggestion=None
    ),
    "open_questions": Pattern(
        name="Открытые вопросы",
        category="positive",
        description="Задавание открытых вопросов для развития диалога",
        examples=["как ты думаешь", "что ты чувствуешь", "расскажи подробнее"],
        suggestion=None
    ),
    "gratitude": Pattern(
        name="Благодарность",
        category="positive",
        description="Выражение благодарности",
        examples=["спасибо", "благодарю", "я ценю", "признателен"],
        suggestion=None
    )
}


class PatternDetector:
    """
    Detects communication patterns in text
    """
    
    def __init__(self):
        self.patterns = PATTERNS
    
    def detect(self, text: str) -> List[Dict]:
        """
        Detect patterns in text
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected patterns
        """
        text_lower = text.lower()
        detected = []
        
        for pattern_id, pattern in self.patterns.items():
            matches = self._find_matches(text_lower, pattern.examples)
            
            if matches:
                detected.append({
                    "id": pattern_id,
                    "name": pattern.name,
                    "category": pattern.category,
                    "description": pattern.description,
                    "matches": matches,
                    "suggestion": pattern.suggestion,
                    "confidence": min(len(matches) * 0.3, 0.9)
                })
        
        return detected
    
    def _find_matches(
        self,
        text: str,
        patterns: List[str]
    ) -> List[str]:
        """Find pattern matches in text"""
        matches = []
        for pattern in patterns:
            if pattern.lower() in text:
                matches.append(pattern)
        return matches
    
    def analyze_conversation(
        self,
        messages: List[Dict]
    ) -> Dict:
        """
        Analyze patterns across conversation
        
        Args:
            messages: List of messages with 'content' and 'role'
            
        Returns:
            Conversation pattern analysis
        """
        user_messages = [m for m in messages if m.get("role") == "user"]
        
        all_patterns = []
        pattern_counts = {"positive": 0, "negative": 0, "neutral": 0}
        pattern_frequency = {}
        
        for msg in user_messages:
            patterns = self.detect(msg.get("content", ""))
            
            for p in patterns:
                all_patterns.append(p)
                category = p["category"]
                pattern_counts[category] += 1
                
                pid = p["id"]
                if pid not in pattern_frequency:
                    pattern_frequency[pid] = {
                        "count": 0,
                        "name": p["name"],
                        "category": p["category"]
                    }
                pattern_frequency[pid]["count"] += 1
        
        # Calculate communication style score
        total = pattern_counts["positive"] + pattern_counts["negative"]
        if total > 0:
            style_score = pattern_counts["positive"] / total
        else:
            style_score = 0.5
        
        # Determine dominant style
        if style_score > 0.6:
            dominant_style = "constructive"
        elif style_score < 0.4:
            dominant_style = "needs_improvement"
        else:
            dominant_style = "mixed"
        
        # Get top issues
        issues = [
            {"pattern": p["name"], "count": p["count"], "suggestion": PATTERNS[pid].suggestion}
            for pid, p in pattern_frequency.items()
            if p["category"] == "negative"
        ]
        issues.sort(key=lambda x: x["count"], reverse=True)
        
        # Get strengths
        strengths = [
            {"pattern": p["name"], "count": p["count"]}
            for pid, p in pattern_frequency.items()
            if p["category"] == "positive"
        ]
        strengths.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "style_score": style_score,
            "dominant_style": dominant_style,
            "pattern_counts": pattern_counts,
            "top_issues": issues[:3],
            "strengths": strengths[:3],
            "total_patterns_detected": len(all_patterns)
        }
    
    def get_suggestions(self, detected_patterns: List[Dict]) -> List[str]:
        """Get improvement suggestions based on detected patterns"""
        suggestions = []
        
        for pattern in detected_patterns:
            if pattern["category"] == "negative" and pattern.get("suggestion"):
                suggestions.append({
                    "issue": pattern["name"],
                    "suggestion": pattern["suggestion"],
                    "examples": pattern["matches"]
                })
        
        return suggestions
