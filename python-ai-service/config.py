"""
Configuration settings for Python AI Service
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Service Configuration
    PYTHON_AI_HOST: str = os.getenv("PYTHON_AI_HOST", "0.0.0.0")
    PYTHON_AI_PORT: int = int(os.getenv("PYTHON_AI_PORT", "8000"))
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # MongoDB (use same default as backend to avoid DB fragmentation)
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/campus-companion")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Backend Integration
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:5000")
    BACKEND_API_KEY: str = os.getenv("BACKEND_API_KEY", "dev-api-key-12345")
    
    # AI Model Configuration
    DEFAULT_AI_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "gpt-3.5-turbo")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Feature Flags
    ENABLE_CONVERSATION_MEMORY: bool = os.getenv("ENABLE_CONVERSATION_MEMORY", "true").lower() == "true"
    ENABLE_AGENT_ACTIONS: bool = os.getenv("ENABLE_AGENT_ACTIONS", "true").lower() == "true"
    ENABLE_VOICE_ASSISTANT: bool = os.getenv("ENABLE_VOICE_ASSISTANT", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

