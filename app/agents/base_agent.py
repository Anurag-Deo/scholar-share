from abc import ABC, abstractmethod
from typing import Any, Dict

from app.services.llm_service import llm_service


class BaseAgent(ABC):
    def __init__(self, name: str, model_type: str = "light"):
        self.name = name
        self.model_type = model_type
        self.llm_service = llm_service

    @abstractmethod
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input and return results"""

    async def generate_response(self, messages: list, temperature: float = 0.7) -> str:
        """Generate LLM response"""
        return await self.llm_service.generate_completion(
            messages=messages,
            model_type=self.model_type,
            temperature=temperature,
        )
