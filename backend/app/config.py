"""
Configuration settings for the AI Newsroom application.
Uses Pydantic settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Database
    database_url: str = "postgresql://newsroom_user:newsroom_pass@localhost:5432/newsroom_db"
    redis_url: str = "redis://localhost:6379"
    
    # JWT Authentication
    secret_key: str = "your-super-secret-jwt-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    
    # AI Services
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    groq_api_key: Optional[str] = None
    
    # News APIs
    news_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    
    # Image Generation
    dalle_api_key: Optional[str] = None
    stability_api_key: Optional[str] = None
    unsplash_access_key: Optional[str] = None
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    
    # Application
    environment: str = "development"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    log_level: str = "INFO"
    
    # File uploads
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings