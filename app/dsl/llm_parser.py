"""LLM-backed parser that conforms to the command schema with retries."""
from __future__ import annotations

import json
from typing import Any, Dict

from pydantic import ValidationError

from .commands import CommandList, CommandType
from .errors import E_SCHEMA_VALIDATION, raise_error
from .llm_provider import BaseLLMProvider, configure_provider


_PROMPT_TEMPLATE = """
You are a CAD command extraction assistant.
Extract drawing commands from the user utterance below.
Return **only** JSON that satisfies this schema: {schema}
Only use the command types draw_circle, draw_line, draw_rect.
Coerce numeric strings to numbers. Use null when data is missing.
User utterance: {utterance}
""".strip()


class LLMParser:
    def __init__(self, provider: BaseLLMProvider | None = None, *, max_retries: int = 3) -> None:
        self.provider = provider or configure_provider()
        self.max_retries = max(1, max_retries)

    @staticmethod
    def _format_prompt(utterance: str, schema: dict[str, Any], errors: list[dict[str, Any]] | None = None) -> str:
        prompt = _PROMPT_TEMPLATE.format(schema=json.dumps(schema, indent=2, sort_keys=True), utterance=utterance)
        if errors:
            prompt += "\nPrevious response failed validation with these issues:\n"
            prompt += json.dumps(errors, indent=2, sort_keys=True)
            prompt += "\nPlease fix them in the next response."
        return prompt

    def parse(self, text: str, context: dict[str, Any] | None = None) -> list[CommandType]:
        schema = CommandList.model_json_schema()
        errors: list[dict[str, Any]] | None = None

        for attempt in range(self.max_retries):
            prompt = self._format_prompt(text, schema, errors)
            provider_context: Dict[str, Any] = {"attempt": attempt}
            if context:
                provider_context.update(context)
            if errors:
                provider_context["errors"] = errors

            payload = self.provider.parse(prompt, schema, context=provider_context)
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError as exc:
                    errors = [{"type": "json_parse_error", "message": str(exc)}]
                    continue

            try:
                envelope = CommandList.model_validate(payload)
            except ValidationError as exc:
                errors = [
                    {
                        "loc": e["loc"],
                        "msg": e["msg"],
                        "type": e["type"],
                    }
                    for e in exc.errors()
                ]
                continue

            return list(envelope.commands)

        detail = json.dumps(errors, indent=2, sort_keys=True) if errors else None
        raise_error(E_SCHEMA_VALIDATION, detail=detail)


def llm_parse(text: str, context: dict[str, Any] | None = None, *, parser: LLMParser | None = None) -> list[CommandType]:
    parser = parser or LLMParser()
    return parser.parse(text, context=context)


__all__ = ["llm_parse", "LLMParser"]
