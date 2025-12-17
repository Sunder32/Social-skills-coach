"""
Application configuration
Loads settings from environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Social Skills Coach"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Backend Server
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8000
    
    # Database - MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "social_skills_coach"
    
    # Redis Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 4000
    
    # FAISS
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    EMBEDDINGS_MODEL: str = "text-embedding-ada-002"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "txt,docx,pdf"
    
    @property
    def DATABASE_URL(self) -> str:
        """Generate async database URL"""
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Generate sync database URL for migrations"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
