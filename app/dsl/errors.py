"""Error codes and exception classes for DSL components."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParseError(Exception):
    """Base error raised when a DSL component fails to parse input."""

    code: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.code}: {self.message}"


E_UNKNOWN_SENTENCE = ("E100", "No canonical rule matched the sentence.")
E_COORDINATE_SYNTAX = ("E101", "Coordinate must be in the form (x,y) with numeric values.")
E_RADIUS_REQUIRED = ("E102", "Circle radius is required for this utterance.")
E_DIMENSION_REQUIRED = ("E103", "Rectangle width and height are required.")
E_PROVIDER_MISSING = ("E200", "LLM provider is not configured.")
E_SCHEMA_VALIDATION = ("E201", "Provider response did not satisfy the command schema.")
E_MEMORY_EXPIRED = ("E300", "Session memory entry has expired.")


def raise_error(error_def: tuple[str, str], detail: str | None = None) -> ParseError:
    """Helper that raises a :class:`ParseError` using an error tuple."""

    code, message = error_def
    if detail:
        message = f"{message} {detail}".strip()
    raise ParseError(code, message)
