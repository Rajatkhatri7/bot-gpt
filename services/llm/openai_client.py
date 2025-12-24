import httpx
from services.llm.base import BaseLLMClient
from core.config import settings


class OpenAIClient(BaseLLMClient):
    async def stream_generate(self, messages, temperature, max_tokens):
        pass