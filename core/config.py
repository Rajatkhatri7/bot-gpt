from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "BOT GPT")
    ENV: str = os.getenv("ENV", "dev")

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ALEMBIC_DATABASE_URL: str = os.getenv("ALEMBIC_DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")  # groq | gemini | ollama
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))

    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY", None)
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    


settings = Settings()
