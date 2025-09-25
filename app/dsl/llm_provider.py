"""Provider abstraction for the LLM-backed parser."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from .errors import E_PROVIDER_MISSING, ParseError, raise_error


class BaseLLMProvider(ABC):
    """Abstract base class representing a model provider."""

    name: str = "base"

    def __init__(self, **config: Any) -> None:
        self.config = config

    @abstractmethod
    def parse(
        self, text: str, schema: dict[str, Any], *, context: dict[str, Any] | None = None
    ) -> dict[str, Any] | str:
        """Parse ``text`` against ``schema`` using the provider."""


class MockProvider(BaseLLMProvider):
    """Simple provider used in tests and development."""

    name = "mock"

    def parse(
        self,
        text: str,
        schema: dict[str, Any],
        *,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:  # pragma: no cover - behaviour exercised indirectly
        # The mock provider expects the prompt to already be a JSON payload.
        try:
            payload = json.loads(text)
            if not isinstance(payload, dict):  # pragma: no cover - defensive
                raise ValueError("Payload must be a JSON object")
            return payload
        except json.JSONDecodeError:
            # For convenience, allow returning the schema stub for deterministic tests.
            return {"commands": []}


ProviderFactory = Callable[[dict[str, Any]], BaseLLMProvider]


class ProviderRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, ProviderFactory] = {}

    def register(self, name: str, factory: ProviderFactory) -> None:
        self._registry[name.lower()] = factory

    def get(self, name: str, config: dict[str, Any]) -> BaseLLMProvider:
        try:
            factory = self._registry[name.lower()]
        except KeyError as exc:  # pragma: no cover - defensive
            raise_error(
                E_PROVIDER_MISSING,
                detail=f"Unknown provider '{name}'.",
                cause=exc,
            )
        return factory(config)

    def available(self) -> list[str]:  # pragma: no cover - trivial
        return sorted(self._registry.keys())


REGISTRY = ProviderRegistry()
REGISTRY.register("mock", lambda cfg: MockProvider(**cfg))

try:  # Register optional LangChain providers when available
    from app.ai import register_langchain_providers

    register_langchain_providers(REGISTRY)
except ParseError:
    # If LangChain dependencies are missing we continue with the mock provider only.
    pass


def configure_provider(name: str | None = None, **overrides: Any) -> BaseLLMProvider:
    """Create a provider based on environment variables and overrides."""

    provider_name = name or os.getenv("AI_PROVIDER") or os.getenv("AI_AUTOCAD_PROVIDER") or "mock"

    if provider_name is None or provider_name.lower() in {"none", "off", "disabled"}:
        raise_error(E_PROVIDER_MISSING, detail="LLM provider disabled.")

    api_key = (
        overrides.pop("api_key", None) or os.getenv("AI_API_KEY") or os.getenv("AI_AUTOCAD_API_KEY")
    )
    model = overrides.pop("model", None) or os.getenv("AI_MODEL")
    temperature = overrides.pop("temperature", None) or os.getenv("AI_TEMPERATURE")

    config: dict[str, Any] = {}
    if api_key:
        config["api_key"] = api_key
    if model:
        config["model"] = model
    if temperature:
        try:
            config["temperature"] = float(temperature)
        except ValueError:  # pragma: no cover - defensive parsing
            config["temperature"] = temperature

    config.update({k: v for k, v in overrides.items() if v is not None})

    return REGISTRY.get(provider_name, config)


__all__ = ["BaseLLMProvider", "MockProvider", "REGISTRY", "configure_provider"]
