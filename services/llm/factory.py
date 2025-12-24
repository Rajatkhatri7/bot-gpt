from core.config import settings
from services.llm.groq_client import GroqClient


def get_llm_client():
    if settings.LLM_PROVIDER == "groq":
        return GroqClient()
    raise ValueError("Unsupported LLM provider")
