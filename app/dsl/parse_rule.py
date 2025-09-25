"""Deterministic parser for the canonical mini-DSL utterances."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from typing import Literal

from pydantic import ValidationError

from .commands import CommandType, Coordinate, DrawCircle, DrawLine, DrawRect
from .errors import (
    E_COORDINATE_SYNTAX,
    E_DIMENSION_REQUIRED,
    E_RADIUS_REQUIRED,
    E_SCHEMA_VALIDATION,
    E_UNKNOWN_SENTENCE,
    ParseError,
    raise_error,
)
from .rules import COORDINATE_TOKEN, RELATIVE_TOKEN, RULES, Rule

_CONNECTOR_RE = re.compile(r"\s*(?:;|\band\b)\s*", flags=re.IGNORECASE)


def _coordinate_from_match(match: re.Match[str], prefix: str) -> Coordinate:
    rel_group = f"{prefix}rel"
    x_group = f"{prefix}x"
    y_group = f"{prefix}y"

    x_raw = match.group(x_group)
    y_raw = match.group(y_group)
    if x_raw is None or y_raw is None:
        raise_error(E_COORDINATE_SYNTAX)

    try:
        x = float(x_raw)
        y = float(y_raw)
    except ValueError as exc:  # pragma: no cover - defensive, regex guards numeric tokens
        raise_error(E_COORDINATE_SYNTAX, detail=str(exc), cause=exc)

    rel_flag = bool(match.group(rel_group))
    return Coordinate(x=x, y=y, system="relative" if rel_flag else "absolute")


def _build_circle(rule: Rule, match: re.Match[str]) -> DrawCircle:
    radius_raw = match.group("radius")
    if radius_raw is None:
        raise_error(E_RADIUS_REQUIRED)
    radius = float(radius_raw)
    center = _coordinate_from_match(match, "center_")
    return DrawCircle(radius=radius, center=center)


def _build_line(rule: Rule, match: re.Match[str]) -> DrawLine:
    start = _coordinate_from_match(match, "start_")
    end = _coordinate_from_match(match, "end_")
    return DrawLine(start=start, end=end)


def _build_rect(rule: Rule, match: re.Match[str]) -> DrawRect:
    width_raw = match.group("width")
    height_raw = match.group("height")
    if width_raw is None or height_raw is None:
        raise_error(E_DIMENSION_REQUIRED)

    anchor: Literal["corner", "center"] = "center" if "center" in rule.name else "corner"
    position = _coordinate_from_match(match, "position_")

    return DrawRect(
        width=float(width_raw), height=float(height_raw), anchor=anchor, position=position
    )


Builder = Callable[[Rule, re.Match[str]], CommandType]

_BUILDERS: dict[str, Builder] = {
    "draw_circle": _build_circle,
    "draw_line": _build_line,
    "draw_rect": _build_rect,
}


def _iter_sentences(text: str) -> Iterator[str]:
    stripped = text.strip()
    if not stripped:
        return iter(())
    return (sentence for raw in _CONNECTOR_RE.split(stripped) if (sentence := raw.strip()))


def _check_coordinate_tokens(text: str) -> None:
    for token in re.findall(r"\([^)]*\)", text):
        if COORDINATE_TOKEN.match(token):
            continue
        if RELATIVE_TOKEN.match(token):
            continue
        raise_error(E_COORDINATE_SYNTAX, detail=f"Problematic token: {token}")


def parse_rule(text: str) -> list[CommandType]:
    """Parse deterministic canonical utterances into :class:`Command` models."""

    commands: list[CommandType] = []
    unmatched_sentences: list[str] = []

    for sentence in _iter_sentences(text):
        for rule in RULES:
            match = rule.pattern.match(sentence)
            if not match:
                continue
            builder = _BUILDERS[rule.command]
            try:
                command = builder(rule, match)
            except ValidationError as exc:
                raise ParseError(E_SCHEMA_VALIDATION[0], str(exc)) from exc
            commands.append(command)
            break
        else:
            unmatched_sentences.append(sentence)

    if unmatched_sentences:
        candidate = " and ".join(unmatched_sentences)
        _check_coordinate_tokens(candidate)
        raise_error(E_UNKNOWN_SENTENCE, detail=f"Input: {candidate}")

    return commands


__all__ = ["parse_rule"]
