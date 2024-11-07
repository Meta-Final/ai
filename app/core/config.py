from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str

    # Server
    HOST: str
    PORT: int

    # Redis
    REDIS_URL: str
    
    # Storage
    STORAGE_PATH: str

    # Authentication
    SECRET_KEY: str
    ALGORITHM: str
    
    QDRANT_CLIENT_URL: str
    QDRANT_CLIENT_PORT: int
    
    EMBEDDING_MODEL: str
    EMBEDDING_DIM: int

    class Config:
        env_file = ".env"

settings = Settings()