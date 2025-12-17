"""
Knowledge base models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Topic(Base):
    """Knowledge topics/categories"""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(100))
    parent_id = Column(Integer, ForeignKey("topics.id"))
    
    order_index = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship("KnowledgeItem", back_populates="topic")
    subtopics = relationship("Topic", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<Topic {self.name}>"


class KnowledgeItem(Base):
    """Knowledge base items"""
    __tablename__ = "knowledge_items"
    
    # FULLTEXT index for search
    __table_args__ = (
        Index('idx_knowledge_fulltext', 'title', 'content', mysql_prefix='FULLTEXT'),
    )

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(500))  # Book/article reference
    
    tags = Column(JSON)  # List of tags
    
    # Vector embedding ID for FAISS
    embedding_id = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="items")

    def __repr__(self):
        return f"<KnowledgeItem {self.title}>"


class Technique(Base):
    """Communication techniques"""
    __tablename__ = "techniques"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    
    when_to_use = Column(JSON)  # List of situations
    steps = Column(JSON)  # List of steps
    examples = Column(JSON)  # List of examples
    common_mistakes = Column(JSON)  # List of mistakes to avoid
    
    # Related data
    situations = Column(JSON)  # Applicable situations
    related_techniques = Column(JSON)  # Related technique names
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Technique {self.name}>"
