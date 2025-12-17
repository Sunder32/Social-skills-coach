"""
Library service - handles knowledge base operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Optional, List

from app.models.knowledge import KnowledgeItem, Topic, Technique
from app.models.user import User
from app.schemas.library import (
    KnowledgeItem as KnowledgeItemSchema,
    KnowledgeSearchResult, TopicResponse, TechniqueResponse
)
from app.services.ai_service import AIService


class LibraryService:
    """Service for knowledge library operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
    
    async def search(
        self,
        query: str,
        topic: Optional[str] = None,
        limit: int = 10
    ) -> KnowledgeSearchResult:
        """
        Hybrid search using MySQL FULLTEXT + FAISS semantic search
        """
        
        # MySQL FULLTEXT search
        sql_results = await self._fulltext_search(query, topic, limit)
        
        # FAISS semantic search
        semantic_results = await self.ai_service.search_knowledge(
            query=query,
            topic=topic,
            limit=limit
        )
        
        # Merge and deduplicate results
        merged = self._merge_results(sql_results, semantic_results, limit)
        
        return KnowledgeSearchResult(
            query=query,
            total_results=len(merged),
            items=merged,
            suggestions=await self._get_search_suggestions(query)
        )
    
    async def _fulltext_search(
        self,
        query: str,
        topic: Optional[str],
        limit: int
    ) -> List[KnowledgeItemSchema]:
        """MySQL FULLTEXT search"""
        
        # Build query
        stmt = select(KnowledgeItem, Topic).join(Topic)
        
        # Add FULLTEXT search condition
        stmt = stmt.where(
            text("MATCH(knowledge_items.title, knowledge_items.content) AGAINST(:query IN NATURAL LANGUAGE MODE)")
        ).params(query=query)
        
        # Topic filter
        if topic:
            stmt = stmt.where(Topic.name == topic)
        
        stmt = stmt.limit(limit)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        return [
            KnowledgeItemSchema(
                id=item.id,
                title=item.title,
                content=item.content,
                source=item.source,
                topic_id=item.topic_id,
                topic_name=topic_obj.name,
                tags=item.tags or [],
                created_at=item.created_at
            )
            for item, topic_obj in rows
        ]
    
    def _merge_results(
        self,
        sql_results: List[KnowledgeItemSchema],
        semantic_results: List[dict],
        limit: int
    ) -> List[KnowledgeItemSchema]:
        """Merge SQL and semantic search results"""
        
        seen_ids = set()
        merged = []
        
        # Add SQL results first
        for item in sql_results:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                merged.append(item)
        
        # Add semantic results
        for result in semantic_results:
            item_id = result.get("id")
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                merged.append(KnowledgeItemSchema(
                    id=item_id,
                    title=result.get("title", ""),
                    content=result.get("content", ""),
                    source=result.get("source"),
                    topic_id=result.get("topic_id", 0),
                    topic_name=result.get("topic_name", ""),
                    tags=result.get("tags", []),
                    relevance_score=result.get("score"),
                    created_at=result.get("created_at")
                ))
        
        return merged[:limit]
    
    async def _get_search_suggestions(self, query: str) -> List[str]:
        """Get related search suggestions"""
        # Simple implementation - could be enhanced with AI
        return []
    
    async def get_topics(self) -> List[TopicResponse]:
        """Get all topics"""
        
        result = await self.db.execute(
            select(Topic, func.count(KnowledgeItem.id).label("item_count"))
            .outerjoin(KnowledgeItem)
            .group_by(Topic.id)
            .order_by(Topic.order_index)
        )
        rows = result.all()
        
        return [
            TopicResponse(
                id=topic.id,
                name=topic.name,
                description=topic.description or "",
                icon=topic.icon,
                item_count=count or 0,
                subtopics=[]
            )
            for topic, count in rows
        ]
    
    async def get_topic_by_id(self, topic_id: int) -> Optional[TopicResponse]:
        """Get topic by ID"""
        
        result = await self.db.execute(
            select(Topic, func.count(KnowledgeItem.id).label("item_count"))
            .outerjoin(KnowledgeItem)
            .where(Topic.id == topic_id)
            .group_by(Topic.id)
        )
        row = result.first()
        
        if not row:
            return None
        
        topic, count = row
        
        # Get subtopics
        subtopics_result = await self.db.execute(
            select(Topic.name).where(Topic.parent_id == topic_id)
        )
        subtopics = [name for (name,) in subtopics_result.all()]
        
        return TopicResponse(
            id=topic.id,
            name=topic.name,
            description=topic.description or "",
            icon=topic.icon,
            item_count=count or 0,
            subtopics=subtopics
        )
    
    async def get_techniques(
        self,
        situation: Optional[str] = None
    ) -> List[TechniqueResponse]:
        """Get communication techniques"""
        
        stmt = select(Technique)
        
        if situation:
            # Filter by situation (JSON contains)
            stmt = stmt.where(
                text("JSON_CONTAINS(situations, :situation)")
            ).params(situation=f'"{situation}"')
        
        result = await self.db.execute(stmt)
        techniques = result.scalars().all()
        
        return [
            TechniqueResponse(
                id=t.id,
                name=t.name,
                description=t.description,
                when_to_use=t.when_to_use or [],
                steps=t.steps or [],
                examples=t.examples or [],
                common_mistakes=t.common_mistakes or [],
                related_techniques=t.related_techniques or [],
                situations=t.situations or []
            )
            for t in techniques
        ]
    
    async def get_technique_by_id(self, technique_id: int) -> Optional[TechniqueResponse]:
        """Get technique by ID"""
        
        result = await self.db.execute(
            select(Technique).where(Technique.id == technique_id)
        )
        t = result.scalar_one_or_none()
        
        if not t:
            return None
        
        return TechniqueResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            when_to_use=t.when_to_use or [],
            steps=t.steps or [],
            examples=t.examples or [],
            common_mistakes=t.common_mistakes or [],
            related_techniques=t.related_techniques or [],
            situations=t.situations or []
        )
    
    async def get_item_by_id(self, item_id: int) -> Optional[KnowledgeItemSchema]:
        """Get knowledge item by ID"""
        
        result = await self.db.execute(
            select(KnowledgeItem, Topic)
            .join(Topic)
            .where(KnowledgeItem.id == item_id)
        )
        row = result.first()
        
        if not row:
            return None
        
        item, topic = row
        
        return KnowledgeItemSchema(
            id=item.id,
            title=item.title,
            content=item.content,
            source=item.source,
            topic_id=item.topic_id,
            topic_name=topic.name,
            tags=item.tags or [],
            created_at=item.created_at
        )
    
    async def get_recommendations(self, user_id: int) -> List[KnowledgeItemSchema]:
        """Get personalized recommendations based on user profile"""
        
        # Get user profile
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.problem_areas:
            # Return general recommendations
            result = await self.db.execute(
                select(KnowledgeItem, Topic)
                .join(Topic)
                .limit(10)
            )
            rows = result.all()
        else:
            # Search based on problem areas
            query = " ".join(user.problem_areas)
            return (await self.search(query, limit=10)).items
        
        return [
            KnowledgeItemSchema(
                id=item.id,
                title=item.title,
                content=item.content[:200] + "...",
                source=item.source,
                topic_id=item.topic_id,
                topic_name=topic.name,
                tags=item.tags or [],
                created_at=item.created_at
            )
            for item, topic in rows
        ]
