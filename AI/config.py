"""
AI Module Configuration
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
import yaml


@dataclass
class ModelConfig:
    """Model configuration"""
    # Base model (можно использовать как основу для fine-tuning)
    base_model: str = "ai-forever/ruGPT-3.5-13B"  # Или меньше: "ai-forever/rugpt3small_based_on_gpt2"
    
    # Our trained model path
    model_path: str = "./models/social_skills_model"
    tokenizer_path: str = "./models/tokenizer"
    
    # Model parameters
    max_length: int = 2048
    hidden_size: int = 768
    num_layers: int = 12
    num_heads: int = 12
    vocab_size: int = 50257
    
    # Generation
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1


@dataclass
class TrainingConfig:
    """Training configuration"""
    # Data
    train_data_path: str = "./data/train"
    eval_data_path: str = "./data/eval"
    
    # Training hyperparameters
    batch_size: int = 4
    gradient_accumulation_steps: int = 8
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    num_epochs: int = 3
    warmup_steps: int = 500
    max_grad_norm: float = 1.0
    
    # LoRA config (for efficient fine-tuning)
    use_lora: bool = True
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    
    # DPO config
    use_dpo: bool = True
    dpo_beta: float = 0.1
    
    # Checkpointing
    checkpoint_dir: str = "./checkpoints"
    save_steps: int = 500
    eval_steps: int = 100
    logging_steps: int = 10
    
    # Hardware
    fp16: bool = True
    bf16: bool = False
    device: str = "cuda"  # or "cpu"


@dataclass
class RAGConfig:
    """RAG configuration"""
    # FAISS
    faiss_index_path: str = "./data/faiss_index"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384
    
    # Retrieval
    top_k: int = 5
    similarity_threshold: float = 0.5
    
    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 50


@dataclass 
class Config:
    """Main configuration"""
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    
    # Paths
    data_dir: str = "./data"
    models_dir: str = "./models"
    logs_dir: str = "./logs"
    
    # API keys (optional, for hybrid approach)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Server
    gradio_port: int = 7860
    gradio_host: str = "0.0.0.0"
    
    @classmethod
    def load(cls, path: str = "config.yaml") -> "Config":
        """Load configuration from YAML file"""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return cls(**data) if data else cls()
        return cls()
    
    def save(self, path: str = "config.yaml"):
        """Save configuration to YAML file"""
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.__dict__, f, default_flow_style=False, allow_unicode=True)


# Global config instance
config = Config.load()


# Create necessary directories
for dir_path in [config.data_dir, config.models_dir, config.logs_dir,
                 config.training.checkpoint_dir, config.training.train_data_path]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
