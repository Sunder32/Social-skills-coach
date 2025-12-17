"""
FAISS Vector Store
Stores and retrieves document embeddings
"""
import numpy as np
import faiss
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from config import config
from core.embeddings import EmbeddingModel


class FAISSStore:
    """
    FAISS-based vector store for semantic search
    """
    
    def __init__(
        self,
        index_path: str = None,
        embedding_model: EmbeddingModel = None
    ):
        self.index_path = index_path or config.rag.faiss_index_path
        self.embedding_model = embedding_model or EmbeddingModel()
        self.embedding_dim = self.embedding_model.embedding_dim
        
        # FAISS index
        self.index = None
        
        # Metadata storage (id -> document info)
        self.metadata = {}
        self.id_counter = 0
        
        # Try to load existing index
        self._load_index()
    
    def _load_index(self):
        """Load index from disk if exists"""
        index_file = os.path.join(self.index_path, "index.faiss")
        meta_file = os.path.join(self.index_path, "metadata.json")
        
        if os.path.exists(index_file) and os.path.exists(meta_file):
            try:
                self.index = faiss.read_index(index_file)
                
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.metadata = {int(k): v for k, v in data["metadata"].items()}
                    self.id_counter = data.get("id_counter", len(self.metadata))
                
                print(f"Loaded FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"Error loading index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create new FAISS index"""
        # Using IndexFlatIP for cosine similarity (with normalized vectors)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.metadata = {}
        self.id_counter = 0
        print("Created new FAISS index")
    
    def save(self):
        """Save index to disk"""
        os.makedirs(self.index_path, exist_ok=True)
        
        index_file = os.path.join(self.index_path, "index.faiss")
        meta_file = os.path.join(self.index_path, "metadata.json")
        
        faiss.write_index(self.index, index_file)
        
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": self.metadata,
                "id_counter": self.id_counter
            }, f, ensure_ascii=False, indent=2)
        
        print(f"Saved index to {self.index_path}")
    
    def add(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> List[int]:
        """
        Add texts to the index
        
        Args:
            texts: List of texts to add
            metadatas: Optional list of metadata dicts
            
        Returns:
            List of assigned IDs
        """
        if not texts:
            return []
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, normalize=True)
        
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Assign IDs
        ids = list(range(self.id_counter, self.id_counter + len(texts)))
        self.id_counter += len(texts)
        
        # Store metadata
        for i, doc_id in enumerate(ids):
            self.metadata[doc_id] = {
                "text": texts[i][:1000],  # Store first 1000 chars
                **(metadatas[i] if metadatas and i < len(metadatas) else {})
            }
        
        # Add to index
        self.index.add(embeddings.astype(np.float32))
        
        return ids
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Query text
            top_k: Number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of results with metadata and scores
        """
        if self.index.ntotal == 0:
            return []
        
        threshold = threshold or config.rag.similarity_threshold
        
        # Get query embedding
        query_embedding = self.embedding_model.encode(query, normalize=True)
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # No more results
                continue
            
            if score < threshold:
                continue
            
            doc_meta = self.metadata.get(idx, {})
            results.append({
                "id": int(idx),
                "score": float(score),
                "text": doc_meta.get("text", ""),
                **{k: v for k, v in doc_meta.items() if k != "text"}
            })
        
        return results
    
    def delete(self, ids: List[int]):
        """Delete documents by IDs (marks as deleted in metadata)"""
        for doc_id in ids:
            if doc_id in self.metadata:
                del self.metadata[doc_id]
        # Note: FAISS IndexFlatIP doesn't support deletion
        # For full deletion, need to rebuild index
    
    def clear(self):
        """Clear all data"""
        self._create_new_index()
    
    @property
    def count(self) -> int:
        """Get number of vectors in index"""
        return self.index.ntotal if self.index else 0
