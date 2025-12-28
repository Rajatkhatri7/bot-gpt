import httpx
from services.llm.base import BaseLLMClient
from core.config import settings


class GroqClient(BaseLLMClient):

    async def stream_generate(self, messages, temperature, max_tokens):
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        yield line.replace("data: ", "")

    async def generate(self, messages, temperature=0, max_tokens=512):
        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
            )

            data = resp.json()
            return data["choices"][0]["message"]["content"]