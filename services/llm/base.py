from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseLLMClient(ABC):

    @abstractmethod
    async def stream_generate(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        ...
