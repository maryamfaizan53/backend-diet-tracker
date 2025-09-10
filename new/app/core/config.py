# py
from pydantic import BaseSettings, Field, validator
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PORT: int = Field(8000)
    LOG_LEVEL: str = Field("INFO")
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_JWT_SECRET: str
    OPENAI_API_KEY: str
    RATE_LIMIT_TOKENS: int = Field(10)
    RATE_LIMIT_RATE: float = Field(1.0)
    STRIPE_SECRET_KEY: Optional[str] = None
    STREAM_CHUNK_SIZE: int = Field(1024)

    class Config:
        env_file = None

    @validator("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_JWT_SECRET", "OPENAI_API_KEY")
    def not_empty(cls, v):
        if not v:
            raise ValueError("Required env var missing")
        return v

_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
