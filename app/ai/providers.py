"""LangChain powered provider integration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pydantic import SecretStr

from app.dsl.errors import E_PROVIDER_MISSING, raise_error
from app.dsl.llm_provider import BaseLLMProvider

if TYPE_CHECKING:  # pragma: no cover - typing only
    from app.dsl.llm_provider import ProviderRegistry


@dataclass(slots=True)
class _HistoryEntry:
    user: str
    response: str


def _resolve_api_key(provider_name: str, explicit: str | SecretStr | None) -> str:
    """Resolve an API key for the given provider."""

    candidates: list[str] = []
    explicit_value = explicit.get_secret_value() if isinstance(explicit, SecretStr) else explicit
    if explicit_value:
        candidates.append(explicit_value)
    provider_name = provider_name.lower()
    if provider_name == "openai":
        candidates.extend([os.getenv("OPENAI_API_KEY", ""), os.getenv("AI_API_KEY", "")])
    elif provider_name in {"groq", "llama3"}:
        candidates.extend([os.getenv("GROQ_API_KEY", ""), os.getenv("AI_API_KEY", "")])
    for value in candidates:
        if value:
            return value
    raise_error(E_PROVIDER_MISSING, detail=f"Missing API key for provider '{provider_name}'.")


def _load_openai(model: str | None, api_key: SecretStr, temperature: float) -> Any:
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:  # pragma: no cover - handled in unit tests
        raise_error(
            E_PROVIDER_MISSING,
            detail="LangChain OpenAI integration is not installed.",
            cause=exc,
        )

    return ChatOpenAI(model=model or "gpt-4o-mini", api_key=api_key, temperature=temperature)


def _load_groq(
    model: str | None,
    api_key: SecretStr,
    temperature: float,
    provider: str,
) -> Any:
    try:
        from langchain_groq import ChatGroq
    except ImportError as exc:  # pragma: no cover - handled in unit tests
        raise_error(
            E_PROVIDER_MISSING,
            detail="LangChain Groq integration is not installed.",
            cause=exc,
        )

    resolved_model = model or ("llama3-70b-8192" if provider == "llama3" else "mixtral-8x7b-32768")
    return ChatGroq(model=resolved_model, api_key=api_key, temperature=temperature)


def _build_llm(
    provider: str,
    *,
    model: str | None,
    api_key: str | SecretStr | None,
    temperature: float,
) -> Any:
    """Instantiate a LangChain chat model based on configuration."""

    key = SecretStr(_resolve_api_key(provider, api_key))
    if provider == "openai":
        return _load_openai(model, key, temperature)
    if provider in {"groq", "llama3"}:
        return _load_groq(model, key, temperature, provider)
    raise_error(E_PROVIDER_MISSING, detail=f"Unsupported provider '{provider}'.")


class LangChainProvider(BaseLLMProvider):
    """Adapter that uses LangChain chat models for parsing."""

    name = "langchain"

    def __init__(
        self,
        llm: Any,
        *,
        provider_name: str,
        history_limit: int = 6,
        **config: Any,
    ) -> None:
        super().__init__(provider_name=provider_name, history_limit=history_limit, **config)
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
        except ImportError as exc:  # pragma: no cover - handled in unit tests
            raise_error(
                E_PROVIDER_MISSING,
                detail="LangChain packages are not installed.",
                cause=exc,
            )

        self.llm = llm
        self.history_limit = history_limit
        self.history: list[_HistoryEntry] = []
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert CAD assistant. Respond with valid JSON that matches the schema.",
                ),
                (
                    "human",
                    "{prompt}",
                ),
            ]
        )
        self._parser = StrOutputParser()

    def _format_prompt(self, prompt: str) -> dict[str, str]:
        if not self.history:
            return {"prompt": prompt}
        history_blob = "\n".join(
            f"User: {entry.user}\nAssistant: {entry.response}"
            for entry in self.history[-self.history_limit :]
        )
        stitched = f"Previous dialogue:\n{history_blob}\n---\n{prompt}"
        return {"prompt": stitched}

    def parse(
        self,
        text: str,
        schema: dict[str, Any],
        *,
        context: dict[str, Any] | None = None,
    ) -> str:
        del schema  # schema already embedded in prompt text
        del context
        rendered = self.prompt | self.llm | self._parser
        message = self._format_prompt(text)
        response = rendered.invoke(message)
        response_text = response if isinstance(response, str) else json.dumps(response)
        self.history.append(_HistoryEntry(user=text, response=response_text))
        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit :]
        return response_text

    @classmethod
    def from_settings(cls, provider: str, config: dict[str, Any]) -> LangChainProvider:
        cfg = dict(config)
        model = cfg.pop("model", None) or cfg.pop("model_name", None)
        temperature = float(cfg.pop("temperature", 0.0) or 0.0)
        history_limit = int(cfg.pop("history_limit", 6) or 6)
        llm = _build_llm(provider, model=model, api_key=cfg.get("api_key"), temperature=temperature)
        return cls(llm, provider_name=provider, history_limit=history_limit, **cfg)


def register_langchain_providers(registry: ProviderRegistry) -> None:
    """Register LangChain backed providers with the shared registry."""

    registry.register("openai", lambda cfg: LangChainProvider.from_settings("openai", cfg))
    registry.register("groq", lambda cfg: LangChainProvider.from_settings("groq", cfg))
    registry.register("llama3", lambda cfg: LangChainProvider.from_settings("llama3", cfg))
