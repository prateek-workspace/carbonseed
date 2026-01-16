from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - Use Neon DB for production
    DATABASE_URL: str = "postgresql://carbonseed:password@localhost:5432/carbonseed"
    
    # JWT Authentication
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Gemini API Integration (optional)
    GEMINI_API_URL: Optional[str] = None
    
    # CORS Settings for Cloudflare Pages deployment
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"


settings = Settings()
