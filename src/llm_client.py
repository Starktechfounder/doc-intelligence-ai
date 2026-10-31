from abc import ABC, abstractmethod
from typing import Optional

class LLMClient(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate response from prompt.

        Args:
            prompt: User query and evidence context.
            system_prompt: Optional system-level instructions.

        Returns:
            Generated text.
        """
        pass

class FakeLLMClient(LLMClient):
    """Deterministic mock client for testing purposes."""

    def __init__(self, canned_response: str = "This is a fake answer."):
        self.canned_response = canned_response
        self.last_prompt = None

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        self.last_prompt = prompt
        return self.canned_response
