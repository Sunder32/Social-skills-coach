"""
Embedding Model - For semantic search and RAG
"""
import torch
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer

from config import config


class EmbeddingModel:
    """
    Embedding model for semantic search
    Uses multilingual sentence transformers
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.rag.embedding_model
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"Embedding model loaded: {self.model_name}")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            # Fallback to a smaller model
            try:
                self.model = SentenceTransformer(
                    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                    device=self.device
                )
            except:
                self.model = None
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Encode texts to embeddings
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            normalize: Normalize embeddings to unit length
            
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize
        )
        
        return embeddings
    
    def similarity(
        self,
        text1: Union[str, List[str]],
        text2: Union[str, List[str]]
    ) -> np.ndarray:
        """
        Compute cosine similarity between texts
        
        Args:
            text1: First text(s)
            text2: Second text(s)
            
        Returns:
            Similarity scores
        """
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        
        # Ensure 2D
        if emb1.ndim == 1:
            emb1 = emb1.reshape(1, -1)
        if emb2.ndim == 1:
            emb2 = emb2.reshape(1, -1)
        
        # Cosine similarity
        return np.dot(emb1, emb2.T)
    
    @property
    def embedding_dim(self) -> int:
        """Get embedding dimension"""
        if self.model is None:
            return config.rag.embedding_dim
        return self.model.get_sentence_embedding_dimension()
