import json

import pytest

from app.dsl.commands import DrawCircle
from app.dsl.errors import ParseError, E_SCHEMA_VALIDATION
from app.dsl.llm_parser import LLMParser
from app.dsl.llm_provider import BaseLLMProvider


class DummyProvider(BaseLLMProvider):
    def __init__(self, responses):
        super().__init__()
        self.responses = list(responses)
        self.contexts = []

    def parse(self, text, schema, *, context=None):
        self.contexts.append(context or {})
        if not self.responses:
            return {}
        response = self.responses.pop(0)
        if callable(response):
            return response(text, schema, context=context)
        return response


def test_llm_parser_successful_coercion():
    provider = DummyProvider(
        [
            {
                "commands": [
                    {
                        "type": "draw_circle",
                        "center": {"x": "10", "y": "20", "system": "absolute"},
                        "radius": "5",
                    }
                ]
            }
        ]
    )
    parser = LLMParser(provider=provider)
    commands = parser.parse("circle please", context={"units": "mm"})
    assert len(commands) == 1
    assert isinstance(commands[0], DrawCircle)
    assert commands[0].radius == 5.0
    assert commands[0].center.x == 10.0
    assert provider.contexts[0]["attempt"] == 0


def test_llm_parser_retry_then_success():
    def invalid_response(text, schema, context=None):
        return {"not": "commands"}

    valid_response = {
        "commands": [
            {
                "type": "draw_circle",
                "center": {"x": 0, "y": 0, "system": "absolute"},
                "radius": 10,
            }
        ]
    }

    provider = DummyProvider([invalid_response, valid_response])
    parser = LLMParser(provider=provider, max_retries=2)
    commands = parser.parse("draw a circle")
    assert len(commands) == 1
    # Ensure retry context captured validation error
    assert len(provider.contexts) == 2
    assert "errors" in provider.contexts[1]


def test_llm_parser_exhausts_retries():
    provider = DummyProvider(["not json", "still wrong"])
    parser = LLMParser(provider=provider, max_retries=2)
    with pytest.raises(ParseError) as exc:
        parser.parse("draw something")
    assert exc.value.code == E_SCHEMA_VALIDATION[0]
