"""
RAG Retriever
Combines FAISS semantic search with knowledge base
"""
from typing import List, Dict, Any, Optional
import asyncio

from config import config
from rag.faiss_store import FAISSStore


class RAGRetriever:
    """
    Retrieval-Augmented Generation retriever
    Combines semantic search with structured knowledge
    """
    
    def __init__(self, faiss_store: FAISSStore = None):
        self.faiss_store = faiss_store or FAISSStore()
    
    async def search(
        self,
        query: str,
        topic: Optional[str] = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base
        
        Args:
            query: Search query
            topic: Optional topic filter
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        top_k = top_k or config.rag.top_k
        
        # Run FAISS search
        results = self.faiss_store.search(query, top_k=top_k * 2)  # Get more for filtering
        
        # Filter by topic if specified
        if topic:
            results = [r for r in results if r.get("topic") == topic]
        
        # Limit results
        results = results[:top_k]
        
        return results
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of documents with 'content' and optional metadata
            
        Returns:
            List of assigned IDs
        """
        texts = []
        metadatas = []
        
        for doc in documents:
            content = doc.get("content", "")
            if not content:
                continue
            
            # Chunk if needed
            chunks = self._chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append({
                    "title": doc.get("title", ""),
                    "topic": doc.get("topic", ""),
                    "topic_id": doc.get("topic_id"),
                    "source": doc.get("source", ""),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
        
        if texts:
            ids = self.faiss_store.add(texts, metadatas)
            self.faiss_store.save()
            return ids
        
        return []
    
    def _chunk_text(
        self,
        text: str,
        chunk_size: int = None,
        overlap: int = None
    ) -> List[str]:
        """Split text into chunks"""
        chunk_size = chunk_size or config.rag.chunk_size
        overlap = overlap or config.rag.chunk_overlap
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end
                for sep in ['. ', '! ', '? ', '\n\n', '\n']:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep > chunk_size // 2:
                        end = start + last_sep + len(sep)
                        break
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks
    
    async def get_context_for_query(
        self,
        query: str,
        max_tokens: int = 2000
    ) -> str:
        """
        Get formatted context for LLM prompt
        
        Args:
            query: User query
            max_tokens: Approximate max tokens for context
            
        Returns:
            Formatted context string
        """
        results = await self.search(query, top_k=5)
        
        if not results:
            return ""
        
        context_parts = []
        total_length = 0
        max_chars = max_tokens * 4  # Approximate chars per token
        
        for result in results:
            text = result.get("text", "")
            title = result.get("title", "")
            
            part = f"### {title}\n{text}\n" if title else f"{text}\n"
            
            if total_length + len(part) > max_chars:
                break
            
            context_parts.append(part)
            total_length += len(part)
        
        return "\n".join(context_parts)
    
    def save(self):
        """Save the index"""
        self.faiss_store.save()
    
    @property
    def document_count(self) -> int:
        """Get number of indexed documents"""
        return self.faiss_store.count
