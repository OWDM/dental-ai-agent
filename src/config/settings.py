"""
Configuration management for the Dental AI Agent
"""

import os
from typing import Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Disable ChromaDB telemetry globally (must be set before chromadb import anywhere)
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # OpenRouter Configuration (Qwen LLM)
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-14b")

    # Jina AI Configuration (Embeddings)
    jina_api_key: str = os.getenv("JINA_API_KEY", "")
    jina_embedding_model: str = os.getenv("JINA_EMBEDDING_MODEL", "jina-embeddings-v3")

    # Supabase Configuration
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", "")

    # Google Calendar Configuration
    google_calendar_credentials_file: str = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "")
    google_calendar_id: str = os.getenv("GOOGLE_CALENDAR_ID", "")

    # Gmail SMTP Configuration
    gmail_address: str = os.getenv("GMAIL_ADDRESS", "")
    gmail_app_password: str = os.getenv("GMAIL_APP_PASSWORD", "")

    # ChromaDB Configuration
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "dental_clinic_faq"

    # Agent Configuration
    max_retries: int = 2
    temperature: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables without errors


# Global settings instance
settings = Settings()
