from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(RuntimeError):
    """Raised when a model provider request cannot be completed cleanly."""


class BaseProvider(ABC):
    @abstractmethod
    def translate(self, *, system_prompt: str, user_prompt: str, model: str) -> str:
        raise NotImplementedError
