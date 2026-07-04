from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator


class ProviderError(RuntimeError):
    """Raised when a model provider request cannot be completed cleanly."""


class BaseProvider(ABC):
    @abstractmethod
    def translate(self, *, system_prompt: str, user_prompt: str, model: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def translate_stream(self, *, system_prompt: str, user_prompt: str, model: str) -> Iterator[str]:
        raise NotImplementedError
