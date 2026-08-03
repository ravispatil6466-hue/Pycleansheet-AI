import os
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    DATA_DIR: str = "./storage/datasets"
    EXPORT_DIR: str = "./storage/exports"
    DATABASE_URL: str = "sqlite:///./pycleansheet.db"

    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.EXPORT_DIR).mkdir(parents=True, exist_ok=True)

def cors_origins_list():
    return [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
