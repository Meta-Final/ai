from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # model_config = {
    #     "env_file": ".env",
    #     "env_file_encoding": "utf-8",
    #     "case_sensitive": False,
    #     "extra": "allow"
    # }
    model_config = {
        "env_file": os.getenv("ENV_FILE", ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "allow"
    }
    # Database
    DATABASE_URL: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_HOST: str
    DATABASE_PORT: str

    # Postgres settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str


    # DATABASE_URL_ADMIN: str
    # POSTGRES_ADMIN_USER: str
    # POSTGRES_ADMIN_PASSWORD: str

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



settings = Settings()